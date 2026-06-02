import sys

from ddgs import DDGS

async def web_search(prompt: str):
     combined_results =""
     search_sites= {
          "github": f"site:github.com {prompt}",
          "stackoverflow": f"site:stackoverflow.com {prompt}",
          "arXiv": f"site:arxiv.org {prompt}",
          "archiveOrg": f"site:archive.org/details/stackexchange {prompt}",
          "genWebSearch": prompt
     }
     with DDGS() as search:
          for s, sites in search_sites.items():
            print(f"Searching {s} \n")
            try:
                results = search.text(sites, max_results=5)
                if results:
                    for i,r in enumerate(results):
                        combined_results += f""" 
                                                ----Data From :{s}---- 
                                              Result {i}: {r['body']}
  
                                            """ 
            except Exception as e:
                sys.stderr.write(f"failed to fetch from {s} \n error Detail: {e}")
     return combined_results.strip()