from io import BytesIO
import requests
import pandas as pd
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from bs4 import BeautifulSoup
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import threading
import time
import copy
from threading import Lock

# For XLS -> XLSX conversion
from pyexcel import get_book

app = Flask(__name__)
CORS(app)

###Custom player section###
# Static player list - modify this list as needed
STATIC_PLAYERS = [
    {
        "id": 1,
        "surname": "durak",
        "given_name": "can",
        "fide_number": "",
        "raw_fullname": "Can Durak"
    },
    {
        "id": 2,
        "surname": "hüseyi̇noğlu",
        "given_name": "ali̇han",
        "fide_number": "",
        "raw_fullname": "Ali̇han Hüseyi̇noğlu"
    },
    {
        "id": 3,
        "surname": "mammadov",
        "given_name": "sadi̇g",
        "fide_number": "",
        "raw_fullname": "Sadi̇g Mammadov"
    },
    {
        "id": 4,
        "surname": "poormosavi̇",
        "given_name": "seyed ki̇an",
        "fide_number": "",
        "raw_fullname": "Seyed Ki̇an Poormosavi̇"
    },
    {
        "id": 5,
        "surname": "mukhammadali̇",
        "given_name": "abdurakhmonov",
        "fide_number": "",
        "raw_fullname": "Abdurakhmonov Mukhammadali̇"
    },
    {
        "id": 6,
        "surname": "schekachi̇khi̇n",
        "given_name": "maksi̇m",
        "fide_number": "",
        "raw_fullname": "Maksi̇m Schekachi̇khi̇n"
    },
    {
        "id": 7,
        "surname": "özsakallioğlu",
        "given_name": "okan",
        "fide_number": "",
        "raw_fullname": "Okan Özsakallioğlu"
    },
    {
        "id": 8,
        "surname": "kamer",
        "given_name": "kayra",
        "fide_number": "",
        "raw_fullname": "Kayra Kamer"
    },
    {
        "id": 9,
        "surname": "bagaturov",
        "given_name": "gi̇orgi̇",
        "fide_number": "",
        "raw_fullname": "Gi̇orgi̇ Bagaturov"
    },
    {
        "id": 10,
        "surname": "darban",
        "given_name": "morteza",
        "fide_number": "",
        "raw_fullname": "Morteza Darban"
    },
    {
        "id": 11,
        "surname": "engi̇n",
        "given_name": "onur çinar",
        "fide_number": "",
        "raw_fullname": "Onur Çinar Engi̇n"
    },
    {
        "id": 12,
        "surname": "ilgaz",
        "given_name": "yusuf kerem",
        "fide_number": "",
        "raw_fullname": "Yusuf Kerem Ilgaz"
    },
    {
        "id": 13,
        "surname": "shoaat",
        "given_name": "ghane",
        "fide_number": "",
        "raw_fullname": "Ghane Shoaat"
    },
    {
        "id": 14,
        "surname": "emi̇nov",
        "given_name": "orkhan",
        "fide_number": "",
        "raw_fullname": "Orkhan Emi̇nov"
    },
    {
        "id": 15,
        "surname": "odeev",
        "given_name": "handszar",
        "fide_number": "",
        "raw_fullname": "Handszar Odeev"
    },
    {
        "id": 16,
        "surname": "di̇ri̇kolu",
        "given_name": "deni̇z",
        "fide_number": "",
        "raw_fullname": "Deni̇z Di̇ri̇kolu"
    },
    {
        "id": 17,
        "surname": "yazici",
        "given_name": "uğur doğa",
        "fide_number": "",
        "raw_fullname": "Uğur Doğa Yazici"
    },
    {
        "id": 18,
        "surname": "özen",
        "given_name": "metehan",
        "fide_number": "",
        "raw_fullname": "Metehan Özen"
    },
    {
        "id": 19,
        "surname": "primbetov",
        "given_name": "kazbek",
        "fide_number": "",
        "raw_fullname": "Kazbek Primbetov"
    },
    {
        "id": 20,
        "surname": "can",
        "given_name": "meli̇h kaan",
        "fide_number": "",
        "raw_fullname": "Meli̇h Kaan Can"
    },
    {
        "id": 21,
        "surname": "tezcan",
        "given_name": "alper",
        "fide_number": "",
        "raw_fullname": "Alper Tezcan"
    },
    {
        "id": 22,
        "surname": "umarov",
        "given_name": "bekhruz",
        "fide_number": "",
        "raw_fullname": "Bekhruz Umarov"
    },
    {
        "id": 23,
        "surname": "nazari̇an",
        "given_name": "arash",
        "fide_number": "",
        "raw_fullname": "Arash Nazari̇an"
    },
    {
        "id": 24,
        "surname": "karademi̇r",
        "given_name": "buğra",
        "fide_number": "",
        "raw_fullname": "Buğra Karademi̇r"
    },
    {
        "id": 25,
        "surname": "darvi̇shi̇",
        "given_name": "mohammad hossei̇n",
        "fide_number": "",
        "raw_fullname": "Mohammad Hossei̇n Darvi̇shi̇"
    },
    {
        "id": 26,
        "surname": "yildiz",
        "given_name": "egehan",
        "fide_number": "",
        "raw_fullname": "Egehan Yildiz"
    },
    {
        "id": 27,
        "surname": "ali̇yev",
        "given_name": "elnur",
        "fide_number": "",
        "raw_fullname": "Elnur Ali̇yev"
    },
    {
        "id": 28,
        "surname": "şi̇mşek",
        "given_name": "ayaz",
        "fide_number": "",
        "raw_fullname": "Ayaz Şi̇mşek"
    },
    {
        "id": 29,
        "surname": "azi̇mi̇",
        "given_name": "ami̇r mohammad",
        "fide_number": "",
        "raw_fullname": "Ami̇r Mohammad Azi̇mi̇"
    },
    {
        "id": 30,
        "surname": "uzdemi̇r",
        "given_name": "ali̇ poyraz",
        "fide_number": "",
        "raw_fullname": "Ali̇ Poyraz Uzdemi̇r"
    },
    {
        "id": 31,
        "surname": "şeker",
        "given_name": "gökhan",
        "fide_number": "",
        "raw_fullname": "Gökhan Şeker"
    },
    {
        "id": 32,
        "surname": "okay",
        "given_name": "koray",
        "fide_number": "",
        "raw_fullname": "Koray Okay"
    },
    {
        "id": 33,
        "surname": "mahdi̇an",
        "given_name": "anousha",
        "fide_number": "",
        "raw_fullname": "Anousha Mahdi̇an"
    },
    {
        "id": 34,
        "surname": "akkara",
        "given_name": "ömer",
        "fide_number": "",
        "raw_fullname": "Ömer Akkara"
    },
    {
        "id": 35,
        "surname": "ergi̇n",
        "given_name": "şahi̇n",
        "fide_number": "",
        "raw_fullname": "Şahi̇n Ergi̇n"
    },
    {
        "id": 36,
        "surname": "dargali",
        "given_name": "hakan",
        "fide_number": "",
        "raw_fullname": "Hakan Dargali"
    },
    {
        "id": 37,
        "surname": "mohandesi̇",
        "given_name": "shahi̇n",
        "fide_number": "",
        "raw_fullname": "Shahi̇n Mohandesi̇"
    },
    {
        "id": 38,
        "surname": "tütüncü",
        "given_name": "ali̇",
        "fide_number": "",
        "raw_fullname": "Ali̇ Tütüncü"
    },
    {
        "id": 39,
        "surname": "özsakallioğlu",
        "given_name": "akin",
        "fide_number": "",
        "raw_fullname": "Akin Özsakallioğlu"
    },
    {
        "id": 40,
        "surname": "akdaş",
        "given_name": "emre",
        "fide_number": "",
        "raw_fullname": "Emre Akdaş"
    },
    {
        "id": 41,
        "surname": "şalci",
        "given_name": "aytuğ celal",
        "fide_number": "",
        "raw_fullname": "Aytuğ Celal Şalci"
    },
    {
        "id": 42,
        "surname": "konduk",
        "given_name": "beki̇r sami̇",
        "fide_number": "",
        "raw_fullname": "Beki̇r Sami̇ Konduk"
    },
    {
        "id": 43,
        "surname": "demi̇rkan",
        "given_name": "mustafa",
        "fide_number": "",
        "raw_fullname": "Mustafa Demi̇rkan"
    },
    {
        "id": 44,
        "surname": "serbes",
        "given_name": "gökay",
        "fide_number": "",
        "raw_fullname": "Gökay Serbes"
    },
    {
        "id": 45,
        "surname": "özkan",
        "given_name": "kaan",
        "fide_number": "",
        "raw_fullname": "Kaan Özkan"
    },
    {
        "id": 46,
        "surname": "akkuş",
        "given_name": "muhammed ali̇",
        "fide_number": "",
        "raw_fullname": "Muhammed Ali̇ Akkuş"
    },
    {
        "id": 47,
        "surname": "bi̇ngül",
        "given_name": "muratcan",
        "fide_number": "",
        "raw_fullname": "Muratcan Bi̇ngül"
    },
    {
        "id": 48,
        "surname": "kalinağa",
        "given_name": "alper",
        "fide_number": "",
        "raw_fullname": "Alper Kalinağa"
    },
    {
        "id": 49,
        "surname": "yardimci",
        "given_name": "can",
        "fide_number": "",
        "raw_fullname": "Can Yardimci"
    },
    {
        "id": 50,
        "surname": "çeli̇k",
        "given_name": "ege yi̇ği̇t",
        "fide_number": "",
        "raw_fullname": "Ege Yi̇ği̇t Çeli̇k"
    },
    {
        "id": 51,
        "surname": "bulgurlu",
        "given_name": "okan",
        "fide_number": "",
        "raw_fullname": "Okan Bulgurlu"
    },
    {
        "id": 52,
        "surname": "kolat",
        "given_name": "ata",
        "fide_number": "",
        "raw_fullname": "Ata Kolat"
    },
    {
        "id": 53,
        "surname": "cankurt",
        "given_name": "arda",
        "fide_number": "",
        "raw_fullname": "Arda Cankurt"
    },
    {
        "id": 54,
        "surname": "karapinar",
        "given_name": "yalin",
        "fide_number": "",
        "raw_fullname": "Yalin Karapinar"
    },
    {
        "id": 55,
        "surname": "çatal",
        "given_name": "uktenur",
        "fide_number": "",
        "raw_fullname": "Uktenur Çatal"
    },
    {
        "id": 56,
        "surname": "öz",
        "given_name": "ege",
        "fide_number": "",
        "raw_fullname": "Ege Öz"
    },
    {
        "id": 57,
        "surname": "kalemler",
        "given_name": "kaan",
        "fide_number": "",
        "raw_fullname": "Kaan Kalemler"
    },
    {
        "id": 58,
        "surname": "kuşluvan",
        "given_name": "yekateri̇na",
        "fide_number": "",
        "raw_fullname": "Yekateri̇na Kuşluvan"
    },
    {
        "id": 59,
        "surname": "akat",
        "given_name": "eli̇fnaz",
        "fide_number": "",
        "raw_fullname": "Eli̇fnaz Akat"
    },
    {
        "id": 60,
        "surname": "onur",
        "given_name": "çi̇ğdem",
        "fide_number": "",
        "raw_fullname": "Çi̇ğdem Onur"
    },
    {
        "id": 61,
        "surname": "yilmazer",
        "given_name": "emi̇r arda",
        "fide_number": "",
        "raw_fullname": "Emi̇r Arda Yilmazer"
    },
    {
        "id": 62,
        "surname": "öztürk",
        "given_name": "efe",
        "fide_number": "",
        "raw_fullname": "Efe Öztürk"
    },
    {
        "id": 63,
        "surname": "akyüz",
        "given_name": "kerem arhan",
        "fide_number": "",
        "raw_fullname": "Kerem Arhan Akyüz"
    },
    {
        "id": 64,
        "surname": "gürbüz",
        "given_name": "bayram",
        "fide_number": "",
        "raw_fullname": "Bayram Gürbüz"
    },
    {
        "id": 65,
        "surname": "kaya",
        "given_name": "enes",
        "fide_number": "",
        "raw_fullname": "Enes Kaya"
    },
    {
        "id": 66,
        "surname": "bayrakoğlu",
        "given_name": "çinar",
        "fide_number": "",
        "raw_fullname": "Çinar Bayrakoğlu"
    },
    {
        "id": 67,
        "surname": "şahi̇n",
        "given_name": "ata sarp",
        "fide_number": "",
        "raw_fullname": "Ata Sarp Şahi̇n"
    },
    {
        "id": 68,
        "surname": "zeyrek",
        "given_name": "ayaz",
        "fide_number": "",
        "raw_fullname": "Ayaz Zeyrek"
    },
    {
        "id": 69,
        "surname": "köseoğlu",
        "given_name": "ömer umut",
        "fide_number": "",
        "raw_fullname": "Ömer Umut Köseoğlu"
    },
    {
        "id": 70,
        "surname": "karacan",
        "given_name": "arda tuna",
        "fide_number": "",
        "raw_fullname": "Arda Tuna Karacan"
    },
    {
        "id": 71,
        "surname": "büker",
        "given_name": "muhi̇tti̇n",
        "fide_number": "",
        "raw_fullname": "Muhi̇tti̇n Büker"
    },
    {
        "id": 72,
        "surname": "sadik",
        "given_name": "muhammed selim",
        "fide_number": "",
        "raw_fullname": "Muhammed Selim Sadik"
    },
    {
        "id": 73,
        "surname": "urun",
        "given_name": "si̇na mete",
        "fide_number": "",
        "raw_fullname": "Si̇na Mete Urun"
    },
    {
        "id": 74,
        "surname": "asilkefeli̇",
        "given_name": "meti̇n",
        "fide_number": "",
        "raw_fullname": "Meti̇n Asilkefeli̇"
    },
    {
        "id": 75,
        "surname": "uzuner",
        "given_name": "tufan can",
        "fide_number": "",
        "raw_fullname": "Tufan Can Uzuner"
    },
    {
        "id": 76,
        "surname": "soyer",
        "given_name": "deni̇z",
        "fide_number": "",
        "raw_fullname": "Deni̇z Soyer"
    },
    {
        "id": 77,
        "surname": "ersoy",
        "given_name": "ahmet",
        "fide_number": "",
        "raw_fullname": "Ahmet Ersoy"
    },
    {
        "id": 78,
        "surname": "dölek",
        "given_name": "gökalp deni̇z",
        "fide_number": "",
        "raw_fullname": "Gökalp Deni̇z Dölek"
    },
    {
        "id": 79,
        "surname": "şeker",
        "given_name": "çinar",
        "fide_number": "",
        "raw_fullname": "Çinar Şeker"
    },
    {
        "id": 80,
        "surname": "demi̇rçi̇n",
        "given_name": "kasim",
        "fide_number": "",
        "raw_fullname": "Kasim Demi̇rçi̇n"
    },
    {
        "id": 81,
        "surname": "gece",
        "given_name": "uğur",
        "fide_number": "",
        "raw_fullname": "Uğur Gece"
    }
]

# Global variables for custom analysis
# Thread-safe globals
custom_players_data = []
custom_analysis_progress = {
    "done": 0,
    "total": 0,
    "analysis_active": False,
    "current_player": None
}
custom_analysis_thread = None
custom_data_lock = Lock()  # Critical addition!

def initialize_custom_players():
    """Initialize the custom players list with static data"""
    global custom_players_data
    
    with custom_data_lock:
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
        
        print(f"Initialized {len(custom_players_data)} custom players")

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

# Thread-safe globals
custom_players_data = []
custom_analysis_progress = {
    "done": 0,
    "total": 0,
    "analysis_active": False,
    "current_player": None
}
custom_analysis_thread = None
custom_data_lock = Lock()  # Critical addition!

def initialize_custom_players():
    """Initialize the custom players list with static data"""
    global custom_players_data
    
    with custom_data_lock:
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
        
        print(f"Initialized {len(custom_players_data)} custom players")

def get_player_by_id(player_id):
    """Thread-safe player lookup"""
    with custom_data_lock:
        for player in custom_players_data:
            if player["id"] == player_id:
                return copy.deepcopy(player)  # Return a copy to avoid reference issues
        return None

def update_player_status(player_id, status, stats=None):
    """Thread-safe player update"""
    with custom_data_lock:
        for player in custom_players_data:
            if player["id"] == player_id:
                player["analysis_status"] = status
                if stats is not None:
                    player["chessbase_stats"] = stats
                print(f"Updated player {player_id}: {status}")
                return True
        return False

def update_progress(done=None, current_player=None, analysis_active=None):
    """Thread-safe progress update"""
    with custom_data_lock:
        if done is not None:
            custom_analysis_progress["done"] = done
        if current_player is not None:
            custom_analysis_progress["current_player"] = current_player
        if analysis_active is not None:
            custom_analysis_progress["analysis_active"] = analysis_active
        
        print(f"Progress: {custom_analysis_progress['done']}/{custom_analysis_progress['total']} - Active: {custom_analysis_progress['analysis_active']}")

def analyze_custom_player(player_id):
    """
    Analyze a single custom player and update their data.
    Uses player_id instead of player object to avoid reference issues.
    """
    player = get_player_by_id(player_id)
    if not player:
        print(f"Player {player_id} not found for analysis")
        return
    
    print(f"Starting analysis for player {player_id}: {player['raw_fullname']}")
    
    # Update status to analyzing
    update_player_status(player_id, "analyzing")
    update_progress(current_player=player["raw_fullname"])
    
    try:
        stats = enhanced_scrape_chessbase_data(
            player["surname"], 
            player["given_name"], 
            player["fide_number"]
        )
        
        if "error" not in stats:
            update_player_status(player_id, "completed", stats)
            print(f"Successfully analyzed player {player_id}")
        else:
            update_player_status(player_id, "failed", stats)
            print(f"Analysis failed for player {player_id}: {stats.get('error', 'Unknown error')}")
            
    except Exception as e:
        error_stats = {"error": str(e)}
        update_player_status(player_id, "failed", error_stats)
        print(f"Exception during analysis of player {player_id}: {e}")
    
    # Update progress
    with custom_data_lock:
        current_done = custom_analysis_progress["done"] + 1
        update_progress(done=current_done, current_player=None)

def analyze_all_custom_players():
    """
    Background task to analyze all custom players.
    Now uses player IDs to avoid reference issues.
    """
    print("Starting background analysis of all custom players")
    
    try:
        # Get list of player IDs to analyze
        with custom_data_lock:
            player_ids = [player["id"] for player in custom_players_data if player["analysis_status"] == "pending"]
        
        print(f"Found {len(player_ids)} players to analyze")
        
        for player_id in player_ids:
            # Check if analysis should continue
            with custom_data_lock:
                should_continue = custom_analysis_progress["analysis_active"]
            
            if not should_continue:
                print("Analysis stopped by user")
                break
            
            analyze_custom_player(player_id)
            
            # Small delay to prevent overwhelming the server
            time.sleep(3)  # Increased delay
            
    except Exception as e:
        print(f"Error in analyze_all_custom_players: {e}")
    finally:
        update_progress(analysis_active=False, current_player=None)
        print("Background analysis completed")

# Routes for Custom Analysis

@app.route("/", methods=["GET"])
def healthcheck():
    return jsonify({
        "Status": "Working"
    }) 

# Updated Routes

@app.route("/api/custom", methods=["GET"])
def get_custom_analysis():
    """
    Get the current state of custom player analysis.
    """
    with custom_data_lock:
        # Return deep copies to avoid reference issues
        players_copy = copy.deepcopy(custom_players_data)
        progress_copy = copy.deepcopy(custom_analysis_progress)
    
    return jsonify({
        "players": players_copy,
        "progress": progress_copy,
        "total_players": len(players_copy)
    })

@app.route("/api/custom/start", methods=["POST"])
def start_custom_analysis():
    """
    Start the custom player analysis process.
    """
    global custom_analysis_thread
    
    with custom_data_lock:
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
        
        print(f"Starting analysis of {len(custom_players_data)} players")
    
    # Start background thread
    custom_analysis_thread = threading.Thread(target=analyze_all_custom_players, daemon=True)
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
    with custom_data_lock:
        if not custom_analysis_progress["analysis_active"]:
            return jsonify({"error": "No analysis is currently running"}), 400
        
        custom_analysis_progress["analysis_active"] = False
        custom_analysis_progress["current_player"] = None
        
        print("Analysis stop requested")
    
    return jsonify({"message": "Analysis stopped"})

@app.route("/api/custom/player/<int:player_id>", methods=["GET"])
def get_custom_player(player_id):
    """
    Get detailed information about a specific custom player.
    """
    player = get_player_by_id(player_id)
    if not player:
        return jsonify({"error": f"No player found with id {player_id}"}), 404
    
    return jsonify(player)

@app.route("/api/custom/reset", methods=["POST"])
def reset_custom_analysis():
    """
    Reset the custom analysis data.
    """
    with custom_data_lock:
        if custom_analysis_progress["analysis_active"]:
            return jsonify({"error": "Cannot reset while analysis is running"}), 400
        
        initialize_custom_players()
        custom_analysis_progress.update({
            "done": 0,
            "total": len(custom_players_data),
            "analysis_active": False,
            "current_player": None
        })
        
        print("Custom analysis reset")
    
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
    print("Custom players initialized")
    app.run(debug=False)  # Debug=False for production