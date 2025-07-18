import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QTextEdit, QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import requests
import json
import logging
from datetime import datetime, timedelta
import random
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# OpenRouter API configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-pro"
# Mock data functions
def get_flights(destination):
    today = datetime.today()
    flights = []
    for i in range(1, 4):
        date = today + timedelta(days=i+2)
        flights.append({
            "airline": f"SkyJet {i}",
            "price": 250 + i * 50,
            "departure": date.strftime('%Y-%m-%d'),
            "arrival": date.strftime('%Y-%m-%d')
        })
    return flights
def suggest_hotels(destination):
    return [
        {"name": f"{destination} Grand Resort", "rating": 4.6, "price": 180},
        {"name": f"{destination} Cozy Stay", "rating": 4.2, "price": 120}
    ]
def call_openrouter_api(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logging.error(f"API call failed: {str(e)}")
        return f"⚠️ I'm currently experiencing technical difficulties. Please try again in a moment."
    except (KeyError, json.JSONDecodeError) as e:
        logging.error(f"Response parsing error: {str(e)}")
        return "⚠️ I encountered an issue processing that request. Could you please rephrase your question?"
def detect_intent(input_text):
    input_text = input_text.lower()
    if any(k in input_text for k in ["destination", "place", "where", "travel", "go to", "recommend"]):
        return "destination"
    elif any(k in input_text for k in ["book", "flight", "hotel", "reserve", "ticket", "accommodation"]):
        return "booking"
    elif any(k in input_text for k in ["explore", "attractions", "food", "activities", "sightseeing", "things to do"]):
        return "explore"
    elif any(k in input_text for k in ["weather", "climate", "temperature", "forecast"]):
        return "weather"
    return "default"
class TravelAssistant(QMainWindow):
    # Predefined country lists based on mood
    MOOD_COUNTRIES = {
        "Relaxing": ["Dubai", "Thailand", "Malaysia", "Singapore"],
        "Romantic": ["Dubai", "Switzerland", "Pakistan", "Malaysia", "United States", "Paris"],
        "Family": ["Dubai", "Malaysia", "England", "France", "Singapore"],
        "Adventure": ["Pakistan", "Switzerland", "Nepal"]
    }
    
    # Predefined country lists based on interest
    INTEREST_COUNTRIES = {
        "Mountains": ["Pakistan", "India", "Nepal", "Switzerland"],
        "Beaches": ["Maldives", "Malaysia", "Singapore", "Dubai", "England"],
        "Nature": ["Pakistan", "Switzerland", "Malaysia", "Paris"],
        "Cities": ["Japan", "United States", "England", "Singapore", "Dubai"],
        "Rural": ["Pakistan", "Vietnam", "Nepal", "Bhutan", "Sudan", "Ethiopia"]
    }
    # Descriptions tailored to mood and interest
    COUNTRY_DESCRIPTIONS = {
        "Dubai": {
            "Relaxing": "Unwind in Dubai's luxurious resorts and serene desert escapes.",
            "Romantic": "Experience romance with stunning skyline views and private beach dinners.",
            "Family": "Fun for all ages with theme parks and family-friendly attractions.",
            "Beaches": "Relax on Dubai's pristine beaches like Jumeirah Beach.",
            "Cities": "Explore the vibrant city life with iconic landmarks like Burj Khalifa."
        },
        "Thailand": {
            "Relaxing": "Bask in the tranquility of Thailand's serene beaches and spa retreats."
        },
        "Malaysia": {
            "Relaxing": "Enjoy Malaysia's laid-back island vibes and lush rainforests.",
            "Romantic": "Discover romantic getaways in Langkawi's stunning resorts.",
            "Family": "Explore Kuala Lumpur's attractions and kid-friendly islands.",
            "Beaches": "Soak up the sun on the beautiful beaches of Penang.",
            "Nature": "Wander through the lush tea plantations of Cameron Highlands."
        },
        "Singapore": {
            "Relaxing": "Find peace in Singapore's gardens and luxurious hotels.",
            "Family": "Kids will love Sentosa Island and Universal Studios.",
            "Beaches": "Enjoy the vibrant shores of Sentosa's beaches.",
            "Cities": "Experience Singapore's futuristic skyline and bustling city life."
        },
        "Switzerland": {
            "Romantic": "Fall in love amidst Switzerland's breathtaking Alps and cozy chalets.",
            "Adventure": "Trek through the majestic Alps for an unforgettable adventure.",
            "Mountains": "Discover the stunning peaks of the Swiss Alps.",
            "Nature": "Stroll through Switzerland's picturesque alpine meadows."
        },
        "Pakistan": {
            "Romantic": "Experience romance in the serene valleys of Hunza.",
            "Adventure": "Challenge yourself with a trek to K2's base camp.",
            "Mountains": "Explore the dramatic peaks of the Karakoram Range.",
            "Nature": "Marvel at the green valleys of Swat and Hunza.",
            "Rural": "Immerse yourself in the rustic charm of Pakistan's northern villages."
        },
        "United States": {
            "Romantic": "Enjoy a romantic escape in Hawaii or New York's vibrant energy.",
            "Cities": "Dive into the dynamic urban scenes of New York or San Francisco."
        },
        "Paris": {
            "Romantic": "Romance awaits in Paris with charming cafes and the Eiffel Tower.",
            "Nature": "Explore the scenic countryside near Paris for a green escape."
        },
        "England": {
            "Family": "Discover family fun in London's museums and countryside adventures.",
            "Beaches": "Relax on the scenic beaches of Brighton.",
            "Cities": "Experience London's vibrant culture and historic landmarks."
        },
        "France": {
            "Family": "Enjoy family-friendly attractions in Paris and the French Riviera."
        },
        "Nepal": {
            "Adventure": "Trek to Mount Everest Base Camp for a thrilling adventure.",
            "Mountains": "Discover the majestic Himalayas in Nepal.",
            "Rural": "Experience the serene rural life in Nepal's villages."
        },
        "Maldives": {
            "Beaches": "Unwind on the Maldives' crystal-clear beaches and overwater bungalows."
        },
        "India": {
            "Mountains": "Explore the rugged beauty of the Himalayas in northern India."
        },
        "Japan": {
            "Cities": "Immerse yourself in Tokyo's cutting-edge urban culture."
        },
        "Vietnam": {
            "Rural": "Discover the tranquil rice fields and villages of Vietnam."
        },
        "Bhutan": {
            "Rural": "Experience Bhutan's peaceful rural landscapes and monasteries."
        },
        "Sudan": {
            "Rural": "Explore the untouched rural beauty of Sudan's countryside."
        },
        "Ethiopia": {
            "Rural": "Discover Ethiopia's rich rural heritage and stunning landscapes."
        }
    }
    
    # Professional responses for various scenarios
    PROFESSIONAL_RESPONSES = {
        "welcome": "Welcome to your personal travel concierge! I'm here to assist you in planning the perfect journey. Please select your travel preferences below.",
        "select_mood_interest": "To provide personalized recommendations, please select both your <b style='color:#4DA8FF'>travel mood</b> and <b style='color:#4DA8FF'>interest</b>.",
        "destination_recommendation": "Based on your preferences, here are my curated destination recommendations:<br><br>",
        "booking_confirmation": "I've prepared the following travel options for your consideration:<br><br>",
        "explore_suggestions": "Here are my recommendations for exploring {destination}:<br><br>",
        "weather_forecast": "Here's the current weather outlook for {destination}:<br><br>",
        "error_generic": "I apologize, but I'm unable to process that request at the moment. Could you please rephrase your question?",
        "error_api": "⚠️ I'm currently experiencing technical difficulties with my information services. Please try again in a moment.",
        "error_no_destination": "To provide specific information, I'll need to know your preferred destination. Would you like me to suggest some destinations first?",
        "error_invalid": "I'm designed to help with travel planning, including destinations, bookings, attractions, and weather. Could you please ask a travel-related question?",
        "help_message": "I'm your professional travel assistant. I can help you with:<br><br>"
                        "• <b style='color:#4DA8FF'>Destination recommendations</b> based on your preferences<br>"
                        "• <b style='color:#4DA8FF'>Flight and hotel bookings</b> for your chosen destination<br>"
                        "• <b style='color:#4DA8FF'>Local attractions and cuisine</b> recommendations<br>"
                        "• <b style='color:#4DA8FF'>Weather forecasts</b> for travel planning<br><br>"
                        "Please select your preferences or ask me a specific question."
    }
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✈️ Travel Concierge")
        self.setMinimumSize(375, 667)
        self.history = []
        self.last_destination = None
        self.moods = ["Relaxing", "Adventure", "Romantic", "Family"]
        self.interests = ["Mountains", "Beaches", "Cities", "Nature"]
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F7FAFF, stop:1 #E6EEFF);
                font-family: 'Segoe UI', Arial;
            }
            QComboBox, QLineEdit, QTextEdit, QPushButton {
                border-radius: 16px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox, QLineEdit, QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #A3C1DA;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            QComboBox:hover, QLineEdit:hover, QTextEdit:hover {
                border: 1px solid #4DA8FF;
            }
            QPushButton {
                background-color: #4DA8FF;
                color: white;
                font-weight: 600;
                border: none;
                padding: 10px 20px;
                transition: background-color 0.2s;
            }
            QPushButton:hover {
                background-color: #3B82F6;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #2563EB;
            }
            QLabel {
                color: #2D3748;
                font-size: 14px;
                padding: 8px;
            }
        """)
        self.init_ui()
    def init_ui(self):
        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        # Dropdowns
        dropdowns = QHBoxLayout()
        dropdowns.setSpacing(12)
        self.mood_box = QComboBox()
        self.mood_box.addItem("🌟 Select Mood")
        self.mood_box.addItems([f" {mood}" for mood in self.moods])
        self.mood_box.setStyleSheet("""
            QComboBox {
                border-radius: 16px;
                padding: 10px;
                background-color: #FFFFFF;
                border: 1px solid #A3C1DA;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
            }
            QComboBox::down-arrow {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAAkUlEQVQ4je2RsQ3CMBCEJ1EEcQAF0AN0EB3EATpIjiM4gBPoIDmK8QBJiJ28S3dP/z/sTI6fH0VR/H0T3eC/3gF2sAOswR+wBr/AOrgA1uAJWIO/YA3+gDX4A9bgD1iDP2AN/oA1+APW4A9Ygz9gDf6ANfgD1uAPWIM/YA3+gDX4A9bgD1iDP2AN/oA1+APW4A9Ygz/gD4i4sX4ABuEAAAAASUVORK5CYII=);
                width: 16px;
                height: 16px;
            }
        """)
        self.mood_box.currentTextChanged.connect(self.update_description)
        self.interest_box = QComboBox()
        self.interest_box.addItem("🌍 Select Interest")
        self.interest_box.addItems([f" {interest}" for interest in self.interests])
        self.interest_box.setStyleSheet("""
            QComboBox {
                border-radius: 16px;
                padding: 10px;
                background-color: #FFFFFF;
                border: 1px solid #A3C1DA;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
            }
            QComboBox::down-arrow {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAAkUlEQVQ4je2RsQ3CMBCEJ1EEcQAF0AN0EB3EATpIjiM4gBPoIDmK8QBJiJ28S3dP/z/sTI6fH0VR/H0T3eC/3gF2sAOswR+wBr/AOrgA1uAJWIO/YA3+gDX4A9bgD1iDP2AN/oA1+APW4A9Ygz9gDf6ANfgD1uAPWIM/YA3+gDX4A9bgD1iDP2AN/oA1+APW4A9Ygz/gD4i4sX4ABuEAAAAASUVORK5CYII=);
                width: 16px;
                height: 16px;
            }
        """)
        self.interest_box.currentTextChanged.connect(self.update_description)
        dropdowns.addWidget(self.mood_box)
        dropdowns.addWidget(self.interest_box)
        layout.addLayout(dropdowns)
        # Description Label
        self.desc_label = QLabel(self.PROFESSIONAL_RESPONSES["welcome"])
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("""
            QLabel {
                color: #2D3748;
                font-size: 14px;
                font-weight: 500;
                padding: 10px;
                background-color: #E6EEFF;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        """)
        layout.addWidget(self.desc_label)
        # Chat Area
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.chat_box.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #A3C1DA;
                border-radius: 16px;
                padding: 12px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial;
            }
        """)
        layout.addWidget(self.chat_box, 1)
        # Input Area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about destinations, bookings, attractions, or weather...")
        self.input_field.returnPressed.connect(self.process_input)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border-radius: 16px;
                padding: 10px;
                border: 1px solid #A3C1DA;
                background-color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4DA8FF;
                box-shadow: 0 0 8px rgba(77,168,255,0.3);
            }
        """)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.process_input)
        send_btn.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                padding: 10px 24px;
                background-color: #4DA8FF;
                color: white;
                font-weight: 600;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3B82F6;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #2563EB;
            }
        """)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)
        # Show welcome message
        self.append_message("assistant", (
            "Hello, traveler! ✈️ I'm your dedicated travel concierge. "
            "To provide personalized recommendations, please select your <b style='color:#4DA8FF'>travel mood</b> and <b style='color:#4DA8FF'>interest</b>, "
            "then ask me about destinations, bookings, attractions, or weather!"
        ))
    def update_description(self):
        mood = self.mood_box.currentText().strip()
        interest = self.interest_box.currentText().strip()
        if mood == "🌟 Select Mood" or interest == "🌍 Select Interest":
            self.desc_label.setText(self.PROFESSIONAL_RESPONSES["select_mood_interest"])
        else:
            self.desc_label.setText(
                f"You're planning a <b style='color:#4DA8FF'>{mood.lower()}</b> journey with a focus on <b style='color:#4DA8FF'>{interest.lower()}</b>. "
                "How may I assist you with your travel plans today?"
            )
    def append_message(self, role, content):
        self.history.append((role, content))
        formatted = ""
        for r, c in self.history:
            tag = "You" if r == "user" else "Travel Concierge"
            bg_color = "#E6EEFF" if r == "user" else "#F7FAFF"
            text_color = "#4DA8FF" if r == "user" else "#2D3748"
            formatted += (
                f"<div style='background-color:{bg_color}; padding:10px; border-radius:12px; margin-bottom:8px;'>"
                f"<b style='color:{text_color}'>{tag}:</b> {c}</div>"
            )
        self.chat_box.setHtml(formatted)
        self.chat_box.verticalScrollBar().setValue(self.chat_box.verticalScrollBar().maximum())
    def handle_destinations(self, mood, interest):
        # Get countries for the selected mood and interest
        mood_countries = self.MOOD_COUNTRIES.get(mood, [])
        interest_countries = self.INTEREST_COUNTRIES.get(interest, [])
        
        # Find common countries
        common_countries = list(set(mood_countries) & set(interest_countries))
        
        # If no common countries, use mood countries as fallback
        if not common_countries:
            common_countries = mood_countries[:3] if len(mood_countries) >= 3 else mood_countries
        
        # Select up to 3 countries randomly
        selected_countries = random.sample(common_countries, min(len(common_countries), 3)) if common_countries else []
        
        # Generate response with descriptions
        destinations = []
        for country in selected_countries:
            description = self.COUNTRY_DESCRIPTIONS.get(country, {}).get(
                mood, self.COUNTRY_DESCRIPTIONS.get(country, {}).get(interest, f"Explore {country} for a wonderful trip!")
            )
            destinations.append({
                "name": country,
                "description": description
            })
        
        # Format the response professionally
        response = (self.PROFESSIONAL_RESPONSES["destination_recommendation"] +
                   "<table style='width:100%; border-collapse: separate; border-spacing: 10px;'>")
        
        for destination in destinations:
            response += f"""
            <tr>
                <td style='width:30%; background-color:#F0F7FF; padding:10px; border-radius:8px;'>
                    <b style='color:#4DA8FF; font-size:16px;'>{destination['name']}</b>
                </td>
                <td style='width:70%; padding:10px; border-radius:8px;'>
                    {destination['description']}
                </td>
            </tr>
            """
        
        response += "</table><br><b style='color:#4DA8FF;'>Would you like more details about any of these destinations?</b>"
        
        self.last_destination = destinations[0]["name"] if destinations else None
        self.append_message("assistant", response)
        
        # Update description with next steps
        if destinations:
            self.desc_label.setText(
                f"I've recommended {len(destinations)} destinations for your {mood.lower()} trip. "
                f"Would you like me to provide <b style='color:#4DA8FF'>booking options</b> for {self.last_destination} "
                f"or <b style='color:#4DA8FF'>explore attractions</b> there?"
            )
        else:
            self.desc_label.setText(
                "I couldn't find destinations matching your preferences. "
                "Please try selecting different options or ask for help."
            )
    def handle_booking(self, text):
        destination = self.last_destination or "Unknown"
        if " in " in text.lower():
            destination = text.lower().split(" in ")[-1].capitalize()
            self.last_destination = destination
        
        # Get flight and hotel data
        flights = get_flights(destination)
        hotels = suggest_hotels(destination)
        
        # Format the response professionally
        response = (self.PROFESSIONAL_RESPONSES["booking_confirmation"] +
                   "<table style='width:100%; border-collapse: separate; border-spacing: 15px;'>")
        
        # Flights section
        response += """
        <tr>
            <td colspan='3' style='background-color:#F0F7FF; padding:12px; border-radius:8px;'>
                <b style='color:#4DA8FF; font-size:16px;'>Flights to {destination}</b>
            </td>
        </tr>
        """.format(destination=destination)
        
        for flight in flights:
            response += f"""
            <tr>
                <td style='padding:8px; border-radius:8px;'><b>{flight['airline']}</b></td>
                <td style='padding:8px; border-radius:8px;'>{flight['departure']}</td>
                <td style='padding:8px; border-radius:8px;'><b>${flight['price']}</b></td>
            </tr>
            """
        
        # Hotels section
        response += """
        <tr>
            <td colspan='3' style='background-color:#F0F7FF; padding:12px; border-radius:8px; margin-top:15px;'>
                <b style='color:#4DA8FF; font-size:16px;'>Recommended Hotels</b>
            </td>
        </tr>
        """
        
        for hotel in hotels:
            response += f"""
            <tr>
                <td style='padding:8px; border-radius:8px;'><b>{hotel['name']}</b></td>
                <td style='padding:8px; border-radius:8px;'>Rating: {hotel['rating']}/5</td>
                <td style='padding:8px; border-radius:8px;'><b>${hotel['price']}/night</b></td>
            </tr>
            """
        
        response += "</table><br><b style='color:#4DA8FF;'>Booking Reference:</b> BOOK{ref_number}<br><br>".format(
            ref_number=datetime.now().strftime('%d%m%H%M'))
        
        response += "<b>Next Steps:</b> Would you like me to help you <b style='color:#4DA8FF'>confirm this booking</b>, " \
                   "provide <b style='color:#4DA8FF'>attractions information</b>, or check the <b style='color:#4DA8FF'>weather forecast</b>?"
        
        self.append_message("assistant", response)
        self.desc_label.setText(
            f"Booking options for {destination} are ready. Would you like to proceed or explore other options?"
        )
    def handle_explore(self, text):
        destination = self.last_destination or "Unknown"
        if " in " in text.lower():
            destination = text.lower().split(" in ")[-1].capitalize()
            self.last_destination = destination
        
        prompt = (f"As a professional travel consultant, suggest 2 must-visit attractions and 2 local dishes in {destination}. "
                 "Provide a brief, engaging description for each. Return the response in a structured JSON format with 'attractions' and 'food' arrays.")
        
        response = call_openrouter_api(prompt)
        
        try:
            suggestions = json.loads(response)
            attractions = suggestions.get("attractions", [])
            food = suggestions.get("food", [])
            
            # Format the response professionally
            response = (self.PROFESSIONAL_RESPONSES["explore_suggestions"].format(destination=destination) +
                       "<table style='width:100%; border-collapse: separate; border-spacing: 15px;'>")
            
            # Attractions section
            response += """
            <tr>
                <td colspan='2' style='background-color:#F0F7FF; padding:12px; border-radius:8px;'>
                    <b style='color:#4DA8FF; font-size:16px;'>Must-Visit Attractions</b>
                </td>
            </tr>
            """
            
            for attraction in attractions:
                response += f"""
                <tr>
                    <td style='width:25%; padding:8px; border-radius:8px;'><b>{attraction.get('name', 'Unknown')}</b></td>
                    <td style='width:75%; padding:8px; border-radius:8px;'>{attraction.get('description', 'Information not available')}</td>
                </tr>
                """
            
            # Food section
            response += """
            <tr>
                <td colspan='2' style='background-color:#F0F7FF; padding:12px; border-radius:8px; margin-top:15px;'>
                    <b style='color:#4DA8FF; font-size:16px;'>Local Cuisine</b>
                </td>
            </tr>
            """
            
            for dish in food:
                response += f"""
                <tr>
                    <td style='width:25%; padding:8px; border-radius:8px;'><b>{dish.get('name', 'Unknown')}</b></td>
                    <td style='width:75%; padding:8px; border-radius:8px;'>{dish.get('description', 'Information not available')}</td>
                </tr>
                """
            
            response += "</table><br><b style='color:#4DA8FF;'>Would you like more details about any of these recommendations?</b>"
            
        except json.JSONDecodeError:
            response = f"⚠️ I apologize, but I'm currently unable to retrieve detailed information about attractions in {destination}. " \
                       "Would you like me to provide general travel advice or check booking options instead?"
        
        self.append_message("assistant", response)
        self.desc_label.setText(
            f"Exploring {destination}'s attractions and cuisine! Would you like booking information or weather details next?"
        )
    def handle_weather(self, text):
        destination = self.last_destination or "Unknown"
        if " in " in text.lower():
            destination = text.lower().split(" in ")[-1].capitalize()
            self.last_destination = destination
        
        prompt = f"Provide a concise weather forecast for {destination} for the next 7 days in a professional, helpful tone."
        weather = call_openrouter_api(prompt)
        
        # Format the response professionally
        response = (self.PROFESSIONAL_RESPONSES["weather_forecast"].format(destination=destination) +
                   f"<div style='background-color:#F0F7FF; padding:15px; border-radius:12px; margin:10px 0;'>{weather}</div>" +
                   "<b style='color:#4DA8FF;'>Is this helpful for your travel planning?</b>")
        
        self.append_message("assistant", response)
        self.desc_label.setText(
            f"Weather information for {destination} provided. Would you like to proceed with bookings or explore more attractions?"
        )
    def process_input(self):
        text = self.input_field.text().strip()
        mood = self.mood_box.currentText().strip()
        interest = self.interest_box.currentText().strip()
        
        if not text:
            return
        
        self.append_message("user", text)
        self.input_field.clear()
        
        if mood == "🌟 Select Mood" or interest == "🌍 Select Interest":
            self.append_message("assistant", self.PROFESSIONAL_RESPONSES["select_mood_interest"])
            return
        
        intent = detect_intent(text)
        
        if intent == "destination":
            self.handle_destinations(mood, interest)
        elif intent == "booking":
            self.handle_booking(text)
        elif intent == "explore":
            self.handle_explore(text)
        elif intent == "weather":
            self.handle_weather(text)
        else:
            self.append_message("assistant", self.PROFESSIONAL_RESPONSES["error_invalid"])
            self.desc_label.setText("I'm here to help with your travel plans. Please ask about destinations, bookings, attractions, or weather.")
            
            # Offer additional assistance
            help_response = self.PROFESSIONAL_RESPONSES["help_message"]
            self.append_message("assistant", help_response)
            
            self.desc_label.setText("I can assist with destinations, bookings, attractions, and weather. How may I help you plan your journey?")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))
    window = TravelAssistant()
    window.show()
    sys.exit(app.exec())
