from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os, json, requests, datetime

pages = [] #instagram username list
chrome_driver = os.getcwd()+"/chromedriver"
options = Options()
options.add_argument('--headless') # comment this line to disable running chrome in background
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images":2})
driver = webdriver.Chrome(chrome_options=options, executable_path=chrome_driver)
for page in pages:
	lastLine = False
	driver.get("https://www.instagram.com/"+page+"/")
	d = json.loads(str(driver.execute_script("return JSON.stringify(window._sharedData);").encode("ascii","ignore")))
	d = d["entry_data"]["ProfilePage"][0]["graphql"]["user"]
	if os.path.exists(d["username"]+"+"+d["id"]+".csv"):
		f = open(d["username"]+"+"+d["id"]+".csv","r")
		lastLine = f.readlines()
		f.close()
		lastLine = lastLine[-1].split(",")[1]
	d["edge_owner_to_timeline_media"]["edges"].reverse()
	for item in d["edge_owner_to_timeline_media"]["edges"]:
		owtim = item["node"]
		if not os.path.exists(d["username"]+"+"+d["id"]+".csv"):
			f = open(d["username"]+"+"+d["id"]+".csv","w")
			f.write("owner,id,typename,shortcode,comment_count,timestamp,display_url,like_count,alt_caption\n")
			f.close()
		f = open(d["username"]+"+"+d["id"]+".csv","a")
		filename = d["id"]+"-"+"".join(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S.%f').split('.'))+".jpg"
		try:
			owtim["accessibility_caption"]
		except Exception:
			owtim["accessibility_caption"]=""
		payload = (
			d["id"],
			owtim["id"],
			owtim["__typename"],
			owtim["shortcode"],
			owtim["edge_media_to_comment"]["count"],
			owtim["taken_at_timestamp"],
			filename,
			owtim["edge_liked_by"]["count"],
			owtim["accessibility_caption"],
			)
		if lastLine:
			if int(owtim["id"])>int(lastLine):
				print(int(owtim["id"]),int(lastLine))
				open(filename,"wb").write(requests.get(owtim["display_url"],allow_redirects=True).content)
				f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%payload)
				print("[+] Added New Entry")
		else:
			open(filename,"wb").write(requests.get(owtim["display_url"],allow_redirects=True).content)
			f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%payload)
			print("[+]")
		f.close()
driver.close()
