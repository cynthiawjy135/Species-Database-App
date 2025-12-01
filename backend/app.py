from flask import Flask, request, jsonify

import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"

@app.get("/api/bundle")
def get_bundle():
    """
    this endpoint returns the full dataset the app needs on first install
    will include en_species, tet_species, media,latest version nnumber
    """
    #client sends version in use... default to 0
    client_version = request.args.get("version", type=int, default=0)

    #get latest version from changelog
    version_resp = (
        supabase.table("changelog")
        .select("version")
        .order("version", desc=True)
        .limit(1)
        .execute()
    )

    #if changelog is empty or something goes wrong
    if version_resp.data is None:
        return jsonify({"error": "reading version failure"}), 500

    #starting with version 1 if no entries yet
    if version_resp.data:
        latest_version = version_resp.data[0]["version"]
    else:
        latest_version = 1
    
    #getting english species
    en_resp = supabase.table("species_en").select("*").execute()
    if en_resp.data is None:
        return jsonify({"error": "couldnt load species_en"}), 500

    #get tetum species
    tet_resp = supabase.table("species_tet").select("*").execute()
    if tet_resp.data is None:
        return jsonify({"error": "couldnt load species_tet"}), 500

    #get media entries
    media_resp = supabase.table("media").select("*").execute()
    if media_resp.data is None:
        return jsonify({"error": "couldnt load media"}), 500

    #retrunign it all as one bundle
    return jsonify({
        "version": latest_version,
        "species_en": en_resp.data,
        "species_tet": tet_resp.data,
        "media":media_resp.data
    })

#       
@app.get("/api/species/changes")
def get_species_changes():
    #app send last version it synced with
    since_version = request.args.get("since_version", type=int)
    if since_version is None:
        return jsonify({"error": "since_version required"}), 400
    
    #getting pagination params... page starts at 1
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=50)

    #puttin gin some limits
    if page < 1: page = 1
    if per_page < 1: per_page =1
    if per_page > 200: per_page = 200

    #supabase uses zero based range
    start = (page -1) *per_page
    end = start + per_page -1

    #get all changelog entries with a version higher than whatclient has
    result = (
        supabase.table("changelog")
        .select("*", count="exact")
        .gt("version", since_version)
        .order("change_id") #keeping results in stable order
        .range(start, end) #applying pagination
        .execute()
    )

    if result.data is None:
        return jsonify({"error": "failed toread changelog"}), 500

    #pagination response
    return jsonify( {
        "total": result.count, #totla matchiong rows
        "page": page,
        "per_page": per_page,
        "data": result.data #just this pages rows
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)