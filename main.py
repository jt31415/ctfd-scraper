import requests
import os
import argparse
import json
import dotenv
import logging

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

def main():

    dotenv.load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", "-u", help="CTFd URL", required=True)
    parser.add_argument("--output", "-o", help="Output directory", required=True)
    args = parser.parse_args()

    BASEURL = args.url + "/api/v1"
    BASEDIR = args.output
    HEADERS = {
        "Authorization": "Token " + os.environ["ACCESS_TOKEN"],
        "Content-Type": "application/json"
    }
    CATEGORIES = {
        "web": "web",
        "crypto": "crypto",
        "reverse engineering": "rev",
        "forensics": "forensics",
        "pwn": "pwn",
        "misc": "misc",
        "season iv beginner's game room": "bgr",
        "???": "mystery"
    }

    challenges = requests.get(BASEURL + "/challenges", headers=HEADERS).json()["data"]

    logging.info(f"Found {len(challenges)} challenges")
    
    for challenge_meta in challenges:

        clean_name = challenge_meta["name"].lower().replace(" ", "-").replace(".", "-")
        logging.info(f"Processing {clean_name}")

        for c in ",'\"!?[]":
            clean_name = clean_name.replace(c, "")

        # create appropriate directories
        challenge_dir = os.path.join(
            BASEDIR, CATEGORIES[challenge_meta["category"].lower()] + "_" + clean_name)
        
        if not os.path.exists(challenge_dir):
            os.makedirs(challenge_dir)
        if not os.path.exists(os.path.join(challenge_dir, "files")):
            os.mkdir(os.path.join(challenge_dir, "files"))

        challenge_data: dict = requests.get(f"{BASEURL}/challenges/{challenge_meta['id']}", headers=HEADERS).json()["data"]

        # write challenge.json info file
        with open(os.path.join(challenge_dir, "challenge.json"), "w") as f:
            json.dump({
                "name": challenge_data.get("name", None),
                "category": challenge_data.get("category", None),
                "points": challenge_data.get("value", None),
                "solves": challenge_data.get("solves", None),
                "description": challenge_data.get("description", None),
                "tags": challenge_data.get("tags", None),
                "hints": challenge_data.get("hints", None)
            }, f, indent=4)

        for file in challenge_data.get("files", []):
            fullurl = args.url + file
            basename = os.path.basename(fullurl)
            basename = basename.split("?")[0]
            filepath = os.path.join(challenge_dir, "files", basename)
            with open(filepath, "wb") as f:
                f.write(requests.get(fullurl, headers=HEADERS).content)

if __name__ == "__main__":
    main()