import threading
from io import BytesIO
import requests
import pandas as pd
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from bs4 import BeautifulSoup
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
# For XLS -> XLSX conversion
from pyexcel import get_book

app = Flask(__name__)
CORS(app)

###Custom player section###
# Static player list - modify this list as needed
STATIC_PLAYERS = [
    {
        "id": 1,
        "surname": "abicic",
        "given_name": "josip",
        "fide_number": "14599619",
        "raw_fullname": "Josip Abicic"
    },
    {
        "id": 2,
        "surname": "agic",
        "given_name": "zejn",
        "fide_number": "16510437",
        "raw_fullname": "Zejn Agic"
    },
    {
        "id": 3,
        "surname": "barbaric",
        "given_name": "matija",
        "fide_number": "79305326",
        "raw_fullname": "Matija Barbaric"
    },
    {
        "id": 4,
        "surname": "belin",
        "given_name": "anton",
        "fide_number": "34610952",
        "raw_fullname": "Anton Belin"
    },
    {
        "id": 5,
        "surname": "belyaletdinov",
        "given_name": "leonard",
        "fide_number": "14641771",
        "raw_fullname": "Leonard Belyaletdinov"
    },
    {
        "id": 6,
        "surname": "brzezina",
        "given_name": "pawel",
        "fide_number": "21078866",
        "raw_fullname": "Pawel Brzezina"
    },
    {
        "id": 7,
        "surname": "buklaho",
        "given_name": "ignacy",
        "fide_number": "21088373",
        "raw_fullname": "Ignacy Buklaho"
    },
    {
        "id": 8,
        "surname": "busic",
        "given_name": "mateo",
        "fide_number": "14439590",
        "raw_fullname": "Mateo Busic"
    },
    {
        "id": 9,
        "surname": "cazacu",
        "given_name": "iustin-nicolas",
        "fide_number": "42206367",
        "raw_fullname": "Iustin-Nicolas Cazacu"
    },
    {
        "id": 10,
        "surname": "celebi",
        "given_name": "mehmet alper",
        "fide_number": "51603934",
        "raw_fullname": "Mehmet Alper Celebi"
    },
    {
        "id": 11,
        "surname": "cominotto",
        "given_name": "mauro",
        "fide_number": "54800004",
        "raw_fullname": "Mauro Cominotto"
    },
    {
        "id": 12,
        "surname": "contala",
        "given_name": "noel",
        "fide_number": "14671212",
        "raw_fullname": "Noel Contala"
    },
    {
        "id": 13,
        "surname": "ejsymont",
        "given_name": "eryk",
        "fide_number": "21089779",
        "raw_fullname": "Eryk Ejsymont"
    },
    {
        "id": 14,
        "surname": "esmer",
        "given_name": "hamza",
        "fide_number": "4007484",
        "raw_fullname": "Hamza Esmer"
    },
    {
        "id": 15,
        "surname": "farkash",
        "given_name": "denys",
        "fide_number": "34178449",
        "raw_fullname": "Denys Farkash"
    },
    {
        "id": 16,
        "surname": "friscic",
        "given_name": "jakov",
        "fide_number": "14587017",
        "raw_fullname": "Jakov Friscic"
    },
    {
        "id": 17,
        "surname": "gazic",
        "given_name": "petar",
        "fide_number": "14430185",
        "raw_fullname": "Petar Gazic"
    },
    {
        "id": 18,
        "surname": "gokce",
        "given_name": "alperen",
        "fide_number": "51697548",
        "raw_fullname": "Alperen Gokce"
    },
    {
        "id": 19,
        "surname": "guo",
        "given_name": "johnny",
        "fide_number": "4007573",
        "raw_fullname": "Johnny Guo"
    },
    {
        "id": 20,
        "surname": "hanas",
        "given_name": "markiyan",
        "fide_number": "34184040",
        "raw_fullname": "Markiyan Hanas"
    },
    {
        "id": 21,
        "surname": "hegedus",
        "given_name": "bernat",
        "fide_number": "17012732",
        "raw_fullname": "Bernat Hegedus"
    },
    {
        "id": 22,
        "surname": "holiga",
        "given_name": "benjamin",
        "fide_number": "79315127",
        "raw_fullname": "Benjamin Holiga"
    },
    {
        "id": 23,
        "surname": "ilko-toth",
        "given_name": "andras",
        "fide_number": "17018234",
        "raw_fullname": "Andras Ilko-Toth"
    },
    {
        "id": 24,
        "surname": "ivanovic",
        "given_name": "leonid",
        "fide_number": "921451",
        "raw_fullname": "Leonid Ivanovic"
    },
    {
        "id": 25,
        "surname": "jokic",
        "given_name": "matej",
        "fide_number": "921227",
        "raw_fullname": "Matej Jokic"
    },
    {
        "id": 26,
        "surname": "kapitanic",
        "given_name": "gabriel",
        "fide_number": "14588960",
        "raw_fullname": "Gabriel Kapitanic"
    },
    {
        "id": 27,
        "surname": "karlovic",
        "given_name": "luka",
        "fide_number": "79305598",
        "raw_fullname": "Luka Karlovic"
    },
    {
        "id": 28,
        "surname": "kartashov",
        "given_name": "nikita",
        "fide_number": "14655454",
        "raw_fullname": "Nikita Kartashov"
    },
    {
        "id": 29,
        "surname": "konopatskyi",
        "given_name": "aleksandr",
        "fide_number": "14656230",
        "raw_fullname": "Aleksandr Konopatskyi"
    },
    {
        "id": 30,
        "surname": "kopacki",
        "given_name": "aleksander",
        "fide_number": "21044481",
        "raw_fullname": "Aleksander Kopacki"
    },
    {
        "id": 31,
        "surname": "kostyukovich",
        "given_name": "ivan",
        "fide_number": "4008421",
        "raw_fullname": "Ivan Kostyukovich"
    },
    {
        "id": 32,
        "surname": "kovac",
        "given_name": "faust",
        "fide_number": "14595338",
        "raw_fullname": "Faust Kovac"
    },
    {
        "id": 33,
        "surname": "krajnc",
        "given_name": "jakob",
        "fide_number": "14656108",
        "raw_fullname": "Jakob Krajnc"
    },
    {
        "id": 34,
        "surname": "krajnc",
        "given_name": "maksim",
        "fide_number": "14652528",
        "raw_fullname": "Maksim Krajnc"
    },
    {
        "id": 35,
        "surname": "krstic",
        "given_name": "david",
        "fide_number": "14654946",
        "raw_fullname": "David Krstic"
    },
    {
        "id": 36,
        "surname": "larion",
        "given_name": "iustin",
        "fide_number": "42213126",
        "raw_fullname": "Iustin Larion"
    },
    {
        "id": 37,
        "surname": "levacic",
        "given_name": "maks",
        "fide_number": "14667347",
        "raw_fullname": "Maks Levacic"
    },
    {
        "id": 38,
        "surname": "levacic",
        "given_name": "matic",
        "fide_number": "14661144",
        "raw_fullname": "Matic Levacic"
    },
    {
        "id": 39,
        "surname": "li",
        "given_name": "changxing",
        "fide_number": "17020182",
        "raw_fullname": "Changxing Li"
    },
    {
        "id": 40,
        "surname": "li",
        "given_name": "yunqi",
        "fide_number": "34610618",
        "raw_fullname": "Yunqi Li"
    },
    {
        "id": 41,
        "surname": "marton-john",
        "given_name": "almos kiran",
        "fide_number": "17013135",
        "raw_fullname": "Almos Kiran Marton-John"
    },
    {
        "id": 42,
        "surname": "mihic",
        "given_name": "peter",
        "fide_number": "14655993",
        "raw_fullname": "Peter Mihic"
    },
    {
        "id": 43,
        "surname": "minga-nagy",
        "given_name": "abel inti",
        "fide_number": "17014298",
        "raw_fullname": "Abel Inti Minga-Nagy"
    },
    {
        "id": 44,
        "surname": "mitrovic",
        "given_name": "vasilije",
        "fide_number": "16509714",
        "raw_fullname": "Vasilije Mitrovic"
    },
    {
        "id": 45,
        "surname": "mueller",
        "given_name": "konstantin",
        "fide_number": "34661778",
        "raw_fullname": "Konstantin Mueller"
    },
    {
        "id": 46,
        "surname": "osinchuk",
        "given_name": "luka",
        "fide_number": "34179119",
        "raw_fullname": "Luka Osinchuk"
    },
    {
        "id": 47,
        "surname": "osmolovskii",
        "given_name": "nikita",
        "fide_number": "4009029",
        "raw_fullname": "Nikita Osmolovskii"
    },
    {
        "id": 48,
        "surname": "osmolovskii",
        "given_name": "philipp",
        "fide_number": "4010345",
        "raw_fullname": "Philipp Osmolovskii"
    },
    {
        "id": 49,
        "surname": "oz",
        "given_name": "ege",
        "fide_number": "26391600",
        "raw_fullname": "Ege Oz"
    },
    {
        "id": 50,
        "surname": "parvu",
        "given_name": "razvan-george",
        "fide_number": "1297066",
        "raw_fullname": "Razvan-George Parvu"
    },
    {
        "id": 51,
        "surname": "pasula",
        "given_name": "milos",
        "fide_number": "920870",
        "raw_fullname": "Milos Pasula"
    },
    {
        "id": 52,
        "surname": "pavlovic",
        "given_name": "aleksej",
        "fide_number": "922425",
        "raw_fullname": "Aleksej Pavlovic"
    },
    {
        "id": 53,
        "surname": "pavlovic",
        "given_name": "david",
        "fide_number": "16509544",
        "raw_fullname": "David Pavlovic"
    },
    {
        "id": 54,
        "surname": "peric",
        "given_name": "david m",
        "fide_number": "921790",
        "raw_fullname": "David M Peric"
    },
    {
        "id": 55,
        "surname": "perunovic",
        "given_name": "uros",
        "fide_number": "921545",
        "raw_fullname": "Uros Perunovic"
    },
    {
        "id": 56,
        "surname": "puhalo",
        "given_name": "damir",
        "fide_number": "79303447",
        "raw_fullname": "Damir Puhalo"
    },
    {
        "id": 57,
        "surname": "puhalo",
        "given_name": "robert",
        "fide_number": "79303455",
        "raw_fullname": "Robert Puhalo"
    },
    {
        "id": 58,
        "surname": "radovic",
        "given_name": "koca",
        "fide_number": "16509846",
        "raw_fullname": "Koca Radovic"
    },
    {
        "id": 59,
        "surname": "rusu",
        "given_name": "lucas",
        "fide_number": "42206472",
        "raw_fullname": "Lucas Rusu"
    },
    {
        "id": 60,
        "surname": "sahin",
        "given_name": "bora",
        "fide_number": "51680491",
        "raw_fullname": "Bora Sahin"
    },
    {
        "id": 61,
        "surname": "sahin",
        "given_name": "sarp",
        "fide_number": "51605066",
        "raw_fullname": "Sarp Sahin"
    },
    {
        "id": 62,
        "surname": "salihbegovic",
        "given_name": "danin",
        "fide_number": "14439719",
        "raw_fullname": "Danin Salihbegovic"
    },
    {
        "id": 63,
        "surname": "seyns",
        "given_name": "odilon",
        "fide_number": "269131",
        "raw_fullname": "Odilon Seyns"
    },
    {
        "id": 64,
        "surname": "shen",
        "given_name": "tingrui",
        "fide_number": "34603441",
        "raw_fullname": "Tingrui Shen"
    },
    {
        "id": 65,
        "surname": "sheng",
        "given_name": "ming",
        "fide_number": "34605258",
        "raw_fullname": "Ming Sheng"
    },
    {
        "id": 66,
        "surname": "shevtsov",
        "given_name": "egor",
        "fide_number": "16510801",
        "raw_fullname": "Egor Shevtsov"
    },
    {
        "id": 67,
        "surname": "solinskyi",
        "given_name": "dmytro",
        "fide_number": "34166319",
        "raw_fullname": "Dmytro Solinskyi"
    },
    {
        "id": 68,
        "surname": "tomazin kosorok",
        "given_name": "tadej",
        "fide_number": "14656183",
        "raw_fullname": "Tadej Tomazin Kosorok"
    },
    {
        "id": 69,
        "surname": "van dooren",
        "given_name": "robbe",
        "fide_number": "290556",
        "raw_fullname": "Robbe Van Dooren"
    },
    {
        "id": 70,
        "surname": "van heinsbergen",
        "given_name": "benjamin",
        "fide_number": "284793",
        "raw_fullname": "Benjamin Van Heinsbergen"
    },
    {
        "id": 71,
        "surname": "van heinsbergen",
        "given_name": "jonathan",
        "fide_number": "276219",
        "raw_fullname": "Jonathan Van Heinsbergen"
    },
    {
        "id": 72,
        "surname": "verbic",
        "given_name": "jan",
        "fide_number": "14655330",
        "raw_fullname": "Jan Verbic"
    },
    {
        "id": 73,
        "surname": "zivic",
        "given_name": "luka",
        "fide_number": "14595265",
        "raw_fullname": "Luka Zivic"
    }
]

# Global variables for custom analysis
custom_players_data = []
custom_analysis_progress = {
    "done": 0,
    "total": 0,
    "analysis_active": False,
    "current_player": None
}
custom_analysis_thread = None

def initialize_custom_players():
    """Initialize the custom players list with static data"""
    global custom_players_data
    custom_players_data = []
    
    for player_data in STATIC_PLAYERS:
        player = {
            "id": player_data["id"],
            "surname": player_data["surname"],
            "given_name": player_data["given_name"],
            "fide_number": player_data["fide_number"],
            "raw_fullname": player_data["raw_fullname"],
            "chessbase_stats": None,
            "analysis_status": "pending"  # pending, analyzing, completed, failed
        }
        custom_players_data.append(player)

def scrape_additional_stats(stats_url):
    """
    Scrape additional statistics from the ChessBase player stats page.
    This function extracts current rating, total games, and performance data.
    """
    try:
        resp = requests.get(stats_url, timeout=10)
        if resp.status_code != 200:
            return {"error": f"Request failed: {resp.status_code}"}
        
        soup = BeautifulSoup(resp.text, "html.parser")
        additional_stats = {}
        
        # Try to find current rating
        rating_elements = soup.find_all(text=lambda t: t and "Rating:" in t)
        if rating_elements:
            for element in rating_elements:
                try:
                    # Extract the number after "Rating:"
                    rating_text = element.strip()
                    if "Rating:" in rating_text:
                        rating = rating_text.split("Rating:")[-1].strip()
                        additional_stats["current_rating"] = rating
                        break
                except:
                    continue
        
        # Try to find total games
        games_elements = soup.find_all(text=lambda t: t and "Games:" in t)
        if games_elements:
            for element in games_elements:
                try:
                    games_text = element.strip()
                    if "Games:" in games_text:
                        games = games_text.split("Games:")[-1].strip()
                        additional_stats["total_games"] = games
                        break
                except:
                    continue
        
        # Try to find performance data (any interesting stats)
        performance_elements = soup.find_all("div", class_="PlayerStats")
        if performance_elements:
            performance_data = []
            for elem in performance_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 10:  # Only meaningful text
                    performance_data.append(text)
            
            if performance_data:
                additional_stats["performance_data"] = " | ".join(performance_data[:3])  # Limit to first 3
        
        return additional_stats
        
    except Exception as e:
        return {"error": str(e)}

def enhanced_scrape_chessbase_data(surname, given_name, fide_number=None):
    """
    Enhanced version of scrape_chessbase_data that includes additional statistics.
    """
    if not surname or not given_name:
        return {"error": "No name to search"}

    # Handle multi-part given names by joining with '%20'
    given_name_encoded = "%20".join(given_name.split())

    # Construct the URL directly to the playerstats endpoint
    stats_url = f"https://players.chessbase.com/en/player/playerstats?first={given_name_encoded}&last={surname}"
    
    try:
        # Get openings data (using existing function)
        openings_data = scrape_player_openings(stats_url)
        
        # Get additional statistics
        additional_stats = scrape_additional_stats(stats_url)
        
        return {
            "profile_stats_url": stats_url,
            "openings": openings_data,
            "additional_stats": additional_stats,
            "analysis_timestamp": int(time.time()),
            "fide_number": fide_number
        }
    except Exception as e:
        return {"error": str(e)}

def analyze_custom_player(player):
    """
    Analyze a single custom player and update their data.
    """
    player["analysis_status"] = "analyzing"
    custom_analysis_progress["current_player"] = player["raw_fullname"]
    
    try:
        stats = enhanced_scrape_chessbase_data(
            player["surname"], 
            player["given_name"], 
            player["fide_number"]
        )
        
        if "error" not in stats:
            player["chessbase_stats"] = stats
            player["analysis_status"] = "completed"
        else:
            player["chessbase_stats"] = stats  # Save the error for debugging
            player["analysis_status"] = "failed"
            
    except Exception as e:
        player["chessbase_stats"] = {"error": str(e)}
        player["analysis_status"] = "failed"
    
    custom_analysis_progress["done"] += 1
    custom_analysis_progress["current_player"] = None

def analyze_all_custom_players():
    """
    Background task to analyze all custom players.
    """
    global custom_analysis_progress
    
    try:
        for player in custom_players_data:
            if not custom_analysis_progress["analysis_active"]:
                break  # Stop if analysis was cancelled
            
            analyze_custom_player(player)
            
            # Small delay to prevent overwhelming the server
            time.sleep(2)
            
    except Exception as e:
        print(f"Error in analyze_all_custom_players: {e}")
    finally:
        custom_analysis_progress["analysis_active"] = False
        custom_analysis_progress["current_player"] = None

# Routes for Custom Analysis

@app.route("/", methods=["GET"])
def healthcheck():
    return jsonify({
        "Status": "Working"
    }) 

@app.route("/api/custom", methods=["GET"])
def get_custom_analysis():
    """
    Get the current state of custom player analysis.
    """
    return jsonify({
        "players": custom_players_data,
        "progress": custom_analysis_progress,
        "total_players": len(custom_players_data)
    })

@app.route("/api/custom/start", methods=["POST"])
def start_custom_analysis():
    """
    Start the custom player analysis process.
    """
    global custom_analysis_thread, custom_analysis_progress
    
    if custom_analysis_progress["analysis_active"]:
        return jsonify({"error": "Analysis is already running"}), 400
    
    # Initialize players if not already done
    if not custom_players_data:
        initialize_custom_players()
    
    # Reset progress
    custom_analysis_progress.update({
        "done": 0,
        "total": len(custom_players_data),
        "analysis_active": True,
        "current_player": None
    })
    
    # Reset all player statuses to pending
    for player in custom_players_data:
        player["analysis_status"] = "pending"
        player["chessbase_stats"] = None
    
    # Start background thread
    custom_analysis_thread = threading.Thread(target=analyze_all_custom_players)
    custom_analysis_thread.start()
    
    return jsonify({
        "message": "Custom analysis started",
        "total_players": len(custom_players_data)
    })

@app.route("/api/custom/stop", methods=["POST"])
def stop_custom_analysis():
    """
    Stop the custom player analysis process.
    """
    global custom_analysis_progress
    
    if not custom_analysis_progress["analysis_active"]:
        return jsonify({"error": "No analysis is currently running"}), 400
    
    custom_analysis_progress["analysis_active"] = False
    custom_analysis_progress["current_player"] = None
    
    return jsonify({"message": "Analysis stopped"})

@app.route("/api/custom/player/<int:player_id>", methods=["GET"])
def get_custom_player(player_id):
    """
    Get detailed information about a specific custom player.
    """
    player = next((p for p in custom_players_data if p["id"] == player_id), None)
    if not player:
        return jsonify({"error": f"No player found with id {player_id}"}), 404
    
    return jsonify(player)

@app.route("/api/custom/reset", methods=["POST"])
def reset_custom_analysis():
    """
    Reset the custom analysis data.
    """
    global custom_analysis_progress
    
    if custom_analysis_progress["analysis_active"]:
        return jsonify({"error": "Cannot reset while analysis is running"}), 400
    
    initialize_custom_players()
    custom_analysis_progress.update({
        "done": 0,
        "total": len(custom_players_data),
        "analysis_active": False,
        "current_player": None
    })
    
    return jsonify({
        "message": "Custom analysis reset",
        "total_players": len(custom_players_data)
    })

# Initialize custom players when the app starts
###End of custom player section###



players_data = []
analysis_progress = {
    "done": 0,
    "total": 0,
    "analysis_active": False
}
player_id_counter = 1

### -------------- 1) Excel Parsing Logic with Dynamic Header Detection --------------

def convert_xls_to_xlsx(file_content: bytes) -> BytesIO:
    """Convert an in-memory .xls file to an in-memory .xlsx file using pyexcel."""
    book = get_book(file_type='xls', file_content=file_content)
    out_stream = BytesIO()
    book.save_to_memory('xlsx', out_stream)
    out_stream.seek(0)
    return out_stream

def parse_excel_with_dynamic_header(xlsx_bytes: bytes) -> pd.DataFrame:
    """
    1) Read the file once with header=None to find the real header row.
    2) Then read again, skipping up to that row, so Pandas uses it as the true header row.
    """
    # First read: no header, read entire sheet
    # (We do this in memory so we don't re-read from disk)
    df_all = pd.read_excel(BytesIO(xlsx_bytes), engine="openpyxl", header=None, dtype=str)

    # We'll look for the row that includes both "SPORCU" and "FIDE NO."
    # (Adjust if you also need "B.NO" or other columns.)
    needed_cols = {"SPORCU", "FIDE NO."}
    header_row = None

    # Search each row for those column headers
    for i in range(len(df_all)):
        # Convert each cell in row i to string, strip, upper/lower, etc.
        row_values = [str(x).strip().upper() for x in df_all.iloc[i].tolist()]
        # If we find *all* needed_cols in that row, we consider it the header row
        if all(any(col in cell for cell in row_values) for col in needed_cols):
            header_row = i
            break

    if header_row is None:
        raise ValueError("Could not find a row containing the required column headers (SPORCU, FIDE NO.).")

    # Second read: skip all rows up to 'header_row', and let that row be the header
    df = pd.read_excel(BytesIO(xlsx_bytes),
                       engine="openpyxl",
                       skiprows=header_row,
                       header=0,
                       dtype=str)
    return df

def convert_turkish_to_english(text):
    """
    Converts Turkish characters in a string to their English equivalents
    and returns the lowercase version of the string.
    """
    turkish_to_english_map = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
        "Ç": "c",
        "Ğ": "g",
        "İ": "i",
        "Ö": "o",
        "Ş": "s",
        "Ü": "u"
    }

    return ''.join(turkish_to_english_map.get(c, c) for c in text).lower()

### -------------- 2) The Flask Routes --------------

@app.route("/api/upload", methods=["POST"])
def upload_excel():
    global player_id_counter

    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Read raw file bytes
    file_bytes = file.read()
    filename_lower = file.filename.lower()

    try:
        # Step 1: Convert .xls to .xlsx if needed
        if filename_lower.endswith(".xls"):
            xlsx_stream = convert_xls_to_xlsx(file_bytes)
            xlsx_bytes = xlsx_stream.read()
        elif filename_lower.endswith(".xlsx"):
            xlsx_bytes = file_bytes
        else:
            return jsonify({"error": "Unsupported file format; use .xls or .xlsx"}), 400

        # Step 2: Parse the DataFrame with dynamic header detection
        df = parse_excel_with_dynamic_header(xlsx_bytes)

        # Clear old data
        players_data.clear()
        player_id_counter = 1

        # Convert each row to a player object
        for index, row in df.iterrows():
            # Safely extract and clean the "SPORCU" field
            full_name = row.get("SPORCU", None)
            if full_name and isinstance(full_name, str):
                full_name = full_name.strip()
            else:
                full_name = ""

            # Safely extract and clean the "FIDE NO." field
            fide_number = row.get("FIDE NO.", None)
            if fide_number and isinstance(fide_number, str):
                fide_number = fide_number.strip()
            else:
                fide_number = ""

            # Skip rows where "SPORCU" is empty (invalid data)
            if not full_name:
                continue
            
            # Split name into "surname" and "given_name"
            name_parts = full_name.split(" ")
            if len(name_parts) >= 2:
                surname = name_parts[0]
                given_name = " ".join(name_parts[1:])
            else:
                surname = ""
                given_name = full_name

            # Convert Turkish characters to English and make lowercase
            surname = convert_turkish_to_english(surname)
            given_name = convert_turkish_to_english(given_name)

            player = {
                "id": player_id_counter,
                "surname": surname,
                "given_name": given_name,
                "fide_number": fide_number,
                "raw_fullname": full_name,
                "chessbase_stats": None,  # Not analyzed yet
            }
            players_data.append(player)
            player_id_counter += 1

        # Prepare progress
        analysis_progress["done"] = 0
        analysis_progress["total"] = len(players_data)
        analysis_progress["analysis_active"] = True

        # Kick off background thread
        thread = threading.Thread(target=analyze_all_players)
        thread.start()

        return jsonify({
            "message": "File uploaded, analysis started",
            "players_count": len(players_data)
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/players", methods=["GET"])
def get_players():
    return jsonify(players_data)


@app.route("/api/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = next((p for p in players_data if p["id"] == player_id), None)
    if not player:
        abort(404, f"No player with id={player_id}")
    return jsonify(player)


@app.route("/api/progress", methods=["GET"])
def get_progress():
    return jsonify(analysis_progress)


def analyze_all_players():
    """
    Background task: scrape ChessBase for each player,
    update players_data, and update progress after each.
    """
    for player in players_data:
        stats = scrape_chessbase_data(player["surname"], player["given_name"], player["fide_number"])
        if "error" not in stats:
            player["chessbase_stats"] = stats
        else:
            player["chessbase_stats"] = stats  # Save the error message for debugging
        analysis_progress["done"] += 1

    analysis_progress["analysis_active"] = False


def scrape_player_openings(url):
    """
    Given a URL (the playerstats endpoint), fetches the page and returns
    a dictionary with keys "white" and "black" listing the player's openings.
    Each opening is represented by a dict with keys:
      - opening_name
      - opening_url
      - average_elo
      - result
    """
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"Request failed: {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")
    openings = {"white": [], "black": []}

    # Find all openings sections
    for section in soup.find_all("div", class_="PlayerOpenings"):
        heading_tag = section.find("h2", class_="PlayerOpeningsHeading")
        if not heading_tag:
            continue
        heading_text = heading_tag.get_text(strip=True)
        if "White" in heading_text:
            color = "white"
        elif "Black" in heading_text:
            color = "black"
        else:
            continue

        # The list of openings is in a div that has inline style (with overflow-y: auto)
        container = section.find("div", style=lambda s: s and "overflow-y" in s)
        if not container:
            continue

        # One approach is to split the container's inner HTML on <hr
        # (each <hr> separates one opening record)
        segments = container.decode_contents().split("<hr")
        for seg in segments:
            # Parse the segment separately
            seg_soup = BeautifulSoup(seg, "html.parser")
            # Look for the opening name (inside an anchor)
            a_tag = seg_soup.find("a")
            if not a_tag:
                continue  # skip if this segment is empty or not valid
            opening_name = a_tag.get_text(strip=True)
            
            # Look for the average Elo line; expect a string like "Average Elo: 1494"
            avg_elo_tag = seg_soup.find(text=lambda t: t and "Average Elo:" in t)
            if avg_elo_tag:
                # Split on colon and strip spaces
                average_elo = avg_elo_tag.split("Average Elo:")[-1].strip()
            else:
                average_elo = None

            # Look for the result text; it is wrapped in one of the score classes.
            result_tag = seg_soup.find(lambda tag: tag.name == "span" and 
                                         tag.get("class") and 
                                         any(x in tag["class"] for x in ["GoodScore", "NormalScore", "BadScore"]))
            if result_tag:
                # Remove the "Result:" part if present
                result_text = result_tag.get_text(strip=True)
                if "Result:" in result_text:
                    result_text = result_text.split("Result:")[-1].strip()
            else:
                result_text = None

            openings[color].append({
                "opening_name": opening_name,
                "average_elo": average_elo,
                "result": result_text,
            })
    return openings


def scrape_chessbase_data(surname, given_name, fide_number=None):
    """
    Scrapes ChessBase data for a player based on surname and given name.
    Now uses the playerstats endpoint to obtain data on openings and statistics.
    """
    if not surname or not given_name:
        return {"error": "No name to search"}

    # Handle multi-part given names by joining with '%20'
    given_name = "%20".join(given_name.split())

    # Construct the URL directly to the playerstats endpoint
    stats_url = f"https://players.chessbase.com/en/player/playerstats?first={given_name}&last={surname}"
    
    try:
        # Instead of parsing a search result, we now call the stats URL directly
        openings_data = scrape_player_openings(stats_url)
        return {
            "profile_stats_url": stats_url,
            "openings": openings_data
        }
    except Exception as e:
        return {"error": str(e)}

### -------------- 3) New Puzzles Endpoint with Real Data --------------

def fetch_chesscom_puzzle():
    """
    Fetches the daily puzzle from Chess.com.
    The Chess.com endpoint returns a flat JSON object.
    Since no rating is provided, we assign a default rating of 2500.
    """
    url = "https://api.chess.com/pub/puzzle"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.93 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Chess.com puzzle API failed: {response.status_code}")
    
    data = response.json()
    # Assign a default rating since Chess.com doesn't provide one.
    default_rating = 2500
    # Use the PGN field as the "solution" (splitting into tokens for now)
    solution = data.get("pgn", "").split()
    return {
        "id": data.get("url", ""),  # Using the URL as an ID, if needed
        "source": "chesscom",
        "rating": default_rating,
        "fen": data.get("fen", ""),
        "solution": solution,
        "description": data.get("title", "Chess.com Daily Puzzle")
    }

def fetch_lichess_puzzle():
    """
    Fetches the daily puzzle from Lichess.
    The response contains a 'puzzle' key with the puzzle details.
    """
    url = "https://lichess.org/api/puzzle/daily"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Lichess puzzle API failed: {response.status_code}")
    
    data = response.json()
    puzzle = data.get("puzzle", {})
    try:
        rating = int(puzzle.get("rating", 0))
    except Exception:
        rating = 0
    solution = puzzle.get("solution", [])
    return {
        "id": puzzle.get("id", ""),
        "source": "lichess",
        "rating": rating,
        "fen": puzzle.get("fen", ""),
        "solution": solution,
        "description": "Lichess Daily Puzzle"
    }

@app.route("/api/hard-puzzles", methods=["GET"])
def get_hard_puzzles():
    """
    Aggregates hard puzzles from Chess.com and Lichess.
    Only puzzles with a rating greater than or equal to a defined threshold are returned.
    """
    threshold = 2000  # Define "hard" as rating >= 2000
    puzzles = []
    try:
        chesscom = fetch_chesscom_puzzle()
        if chesscom.get("rating", 0) >= threshold:
            puzzles.append(chesscom)
    except Exception as e:
        print("Error fetching Chess.com puzzle:", e)
    try:
        lichess = fetch_lichess_puzzle()
        if lichess.get("rating", 0) >= threshold:
            puzzles.append(lichess)
    except Exception as e:
        print("Error fetching Lichess puzzle:", e)
    return jsonify(puzzles)

# Coordinates for Mersin, Turkey
MERSIN_COORDINATES = (36.8121, 34.6415)

def fetch_tsf_tournaments():
    url = "https://www.tsf.org.tr/kaynaklar/etkinlik-takvimi"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    tournaments = []

    # Find all month tables
    month_tables = soup.find_all('table', cellspacing="2", align="center", cellpadding="0", border="0", width="100%")
    
    for table in month_tables:
        # Get month name from the header
        month_header = table.find('td', style=lambda s: s and "background:#287a92" in s)
        if not month_header:
            continue
        
        month_name = month_header.text.strip()
        
        # Find all tournament rows
        rows = table.find_all('tr')
        # Skip the header rows (first two rows)
        for row in rows[2:]:
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
                
            # Extract tournament details
            name_cell = cells[0]
            name_link = name_cell.find('a')
            
            if name_link:
                name = name_link.text.strip()
                official_url = name_link['href']
            else:
                # If no link, try to find the text directly
                name_font = name_cell.find('font')
                if name_font:
                    name = name_font.text.strip()
                else:
                    name = name_cell.text.strip()
                official_url = ""
                
            place = cells[1].text.strip()
            start_date_str = cells[2].text.strip()
            end_date_str = cells[3].text.strip()
            
            # Parse dates
            try:
                # Convert Turkish month names to numbers
                turkish_months = {
                    'Ocak': '01', 'Şubat': '02', 'Mart': '03', 'Nisan': '04',
                    'Mayıs': '05', 'Haziran': '06', 'Temmuz': '07', 'Ağustos': '08',
                    'Eylül': '09', 'Ekim': '10', 'Kasım': '11', 'Aralık': '12'
                }
                
                # Parse start date
                if start_date_str:
                    day, month_year = start_date_str.split(' ', 1)
                    for tr_month, num_month in turkish_months.items():
                        if tr_month in month_year:
                            month_year = month_year.replace(tr_month, num_month)
                            break
                    month, year = month_year.split(' ')
                    start_date = datetime.strptime(f"{day.strip()}.{month.strip()}.{year.strip()}", "%d.%m.%Y")
                else:
                    start_date = None
                    
                # Parse end date
                if end_date_str:
                    day, month_year = end_date_str.split(' ', 1)
                    for tr_month, num_month in turkish_months.items():
                        if tr_month in month_year:
                            month_year = month_year.replace(tr_month, num_month)
                            break
                    month, year = month_year.split(' ')
                    end_date = datetime.strptime(f"{day.strip()}.{month.strip()}.{year.strip()}", "%d.%m.%Y")
                else:
                    end_date = None
                    
            except (ValueError, IndexError) as e:
                print(f"Error parsing dates for tournament '{name}': {e}")
                start_date = None
                end_date = None
                
            tournaments.append({
                'name': name,
                'place': place,
                'start_date': start_date,
                'end_date': end_date,
                'month': month_name,
                'official_url': official_url
            })
    
    return tournaments

def calculate_score(tournament):
    tournament_coordinates = geocode_location(tournament['place'])
    if not tournament_coordinates:
        return float('inf')  # Assign a high score if location is unknown

    # Calculate distance to Mersin
    distance_km = geodesic(MERSIN_COORDINATES, tournament_coordinates).kilometers

    # Calculate days until the tournament
    days_until = (tournament['date'] - datetime.now()).days

    # Weight factors
    location_weight = 0.7
    date_weight = 0.3

    # Normalize and calculate score
    location_score = distance_km  # Assuming closer is better
    date_score = max(days_until, 0)  # Non-negative; sooner is better
    score = (location_weight * location_score) + (date_weight * date_score)
    return score

def geocode_location(location):
    geolocator = Nominatim(user_agent="tournament_locator")
    try:
        geo_location = geolocator.geocode(location)
        if geo_location:
            return (geo_location.latitude, geo_location.longitude)
        else:
            print(f"Geocoding failed for location: {location}")
            return None
    except Exception as e:
        print(f"Error during geocoding for location '{location}': {e}")
        return None

@app.route("/api/tournaments", methods=["GET"])
def get_tournaments():
    print("Fetching tournaments...")
    tournaments = fetch_tsf_tournaments()
    
    # Filter for future tournaments and prepare for JSON serialization
    current_date = datetime.now()
    result_tournaments = []
    
    for tournament in tournaments:
        # Skip tournaments with no start date
        if not tournament['start_date']:
            continue
            
        # Only include future tournaments
        if tournament['start_date'] > current_date:
            # Convert datetime objects to strings for JSON serialization
            tournament_data = {
                'name': tournament['name'],
                'place': tournament['place'],
                'start_date': tournament['start_date'].strftime('%Y-%m-%d'),
                'end_date': tournament['end_date'].strftime('%Y-%m-%d') if tournament['end_date'] else None,
                'month': tournament['month'],
                'official_url': tournament['official_url'],
            }
            result_tournaments.append(tournament_data)
    
    # Sort by start date (ascending)
    sorted_tournaments = sorted(result_tournaments, key=lambda x: x['start_date'])
    
    return jsonify(sorted_tournaments)

if __name__ == "__main__":
    initialize_custom_players()
    print("Players initialized")
