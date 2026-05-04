import json
import urllib.request
url = "https://api.snooker.org/?t=10&st=p&s=2025"
request = urllib.request.Request(url)
request.add_header("X-Requested-By", "AdamTinker319")
response = urllib.request.urlopen(request)
data = json.loads(response.read())
url2 = "https://api.snooker.org/?rt=MoneyRankings&s=2025"
request2 = urllib.request.Request(url2)
request2.add_header("X-Requested-By", "AdamTinker319")
response2 = urllib.request.urlopen(request2)
rankings = json.loads(response2.read())
player_country = {}
for player in data:
    player_country[player["ID"]] = player["Nationality"]
country_points = {}
for ranking in rankings:
    player_id = ranking["PlayerID"]
    points = ranking["Sum"]
    country = player_country[player_id]
    if country not in country_points:
        country_points[country] = 0
    country_points[country] = country_points[country] + points
sorted_countries = sorted(country_points.items(), key=lambda x: x[1], reverse=True)
for position, (country, points) in enumerate(sorted_countries, start=1):
    print(position, country, "-", f"£{points:,}")