import asyncio
import re
import requests
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import html

class MaRDIClient:
    def __init__(self):
        self.sparql_url = "https://query.portal.mardi4nfdi.de/sparql"
        self.api_url = "https://portal.mardi4nfdi.de/w/api.php"
        self.sparql = SPARQLWrapper(self.sparql_url)
        self.sparql.addCustomHttpHeader("User-Agent", "MaRDI-MCP-Agent/1.0")

    def _extract_tex(self, math_ml_string):
        """
        Extracts clean LaTeX from a MaRDI MathML string.
        Handles XML tags, HTML entities, and MediaWiki formatting artifacts.
        """
        if not math_ml_string or not isinstance(math_ml_string, str):
            return ""

        # 1. Regex to find content inside <annotation encoding="application/x-tex">...</annotation>
        # We use a list of patterns to be safe, but the first one is the standard MaRDI format.
        patterns = [
            r'<annotation encoding="application/x-tex"[^>]*>(.*?)</annotation>',
            r'<annotation encoding="application/x-latex"[^>]*>(.*?)</annotation>', 
            r'<annotation[^>]+>(.*?)</annotation>'  # Fallback: any annotation
        ]
        
        raw_tex = ""
        for pat in patterns:
            match = re.search(pat, math_ml_string, re.DOTALL | re.IGNORECASE)
            if match:
                raw_tex = match.group(1)
                break  # Stop as soon as we find a match
        
        if not raw_tex:
            return ""  # Could not find any TeX annotation

        # 2. Unescape HTML Entities (Critical for <, >, &)
        # Converts "&lt;" -> "<", "&gt;" -> ">", "&amp;" -> "&"
        clean_tex = html.unescape(raw_tex).strip()

        # 3. Remove MediaWiki/MathJax artifacts
        # Common wrappers that are useless for LLMs/Solders
        artifacts = [
            r"{\displaystyle", 
            r"{\textstyle", 
            r"\displaystyle", 
            r"\textstyle"
        ]
        for artifact in artifacts:
            clean_tex = clean_tex.replace(artifact, "")

        # 4. Balance Braces (Simple Heuristic)
        # The .replace() above often leaves trailing braces "}}" from the original wrapper.
        # If we have more closing braces than opening ones, strip them from the end.
        while clean_tex.count('}') > clean_tex.count('{'):
            if clean_tex.endswith('}'):
                clean_tex = clean_tex[:-1]
            else:
                # If the extra brace is somewhere in the middle (unlikely but possible),
                # we stop to avoid breaking valid nested math.
                break

        return clean_tex.strip()


    def search_entity_id(self, term):
        params = {
            'action': 'wbsearchentities',
            'search': term,
            'language': 'en',
            'type': 'item',
            'limit': 1,
            'format': 'json'
        }
        try:
            resp = requests.get(self.api_url, params=params, headers={'User-Agent': 'MaRDI-MCP'})
            data = resp.json()
            if data.get('search'):
                return data['search'][0]
            return None
        except Exception:
            return None

    # --- NEW: Internal method to get raw data (List of Dicts) ---
    async def _fetch_raw_formulas(self, concept_term: str, limit: int = 20):
        """Fetches the raw list of formula dictionaries."""
        entity = self.search_entity_id(concept_term)
        if not entity:
            return []

        concept_id = entity['id']
        
        # Improved Query with Description
        query = f"""
        SELECT ?formula ?formulaLabel ?mathExpression ?description WHERE {{
          ?formula wdt:P4 wd:{concept_id} .
          ?formula wdt:P15 ?mathExpression .
          OPTIONAL {{ 
            ?formula schema:description ?description . 
            FILTER(LANG(?description) = "en") 
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        
        loop = asyncio.get_running_loop()
        try:
            results = await loop.run_in_executor(None, lambda: self.sparql.query().convert())
        except Exception as e:
            print(f"Error: {e}")
            return []

        bindings = results["results"]["bindings"]
        cleaned_results = []
        
        for b in bindings:
            raw_xml = b.get("mathExpression", {}).get("value", "")
            tex = self._extract_tex(raw_xml)
            
            # Only add if we found some content
            cleaned_results.append({
                "id": b.get("formulaLabel", {}).get("value", "Unknown"),
                "tex": tex,
                "description": b.get("description", {}).get("value", ""),
                "url": b.get("formula", {}).get("value", "")
            })
            
        return cleaned_results

    # --- The Method triggering your error (FIXED) ---
    async def filter_formulas_for_agent(self, concept: str):
        """
        Returns a JSON string of the top ranked formulas.
        """
        # 1. Get the RAW list of dicts (not a string!)
        raw_items = await self._fetch_raw_formulas(concept)
        
        valid_results = []
        for item in raw_items:
            # item is now guaranteed to be a dict, so item['tex'] works
            if not item['tex'] or len(item['tex']) < 5:
                continue
            
            # Heuristic: Deprioritize complex inequalities if simple definition exists
            is_inequality = any(c in item['tex'] for c in ['<', '>', '\\le', '\\ge'])
            
            valid_results.append({
                "id": item['id'],
                "tex": item['tex'].replace('}}', ''),#for removing the leftoverclosing braces
                "description": item['description'],
                "link": item['url'],
                "type": "condition/bound" if is_inequality else "definition/identity"
            })
        
        # 2. Limit to top 10 and return as JSON string for the Agent
        return json.dumps(valid_results[:10], indent=2)

if __name__ == "__main__":
    # This should now print a valid JSON string
    print(asyncio.run(MaRDIClient().filter_formulas_for_agent("gamma function")))
