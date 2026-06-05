from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import requests

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roadsoul.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

WEATHER_API_KEY = 'adb77012e4b746b87a187b36605c3dec'

class Stop(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    corridor        = db.Column(db.String(50), nullable=False)
    name            = db.Column(db.String(100), nullable=False)
    lat             = db.Column(db.Float, nullable=False)
    lng             = db.Column(db.Float, nullable=False)
    description     = db.Column(db.Text, nullable=False)
    tags            = db.Column(db.String(200), nullable=False)
    labels          = db.Column(db.String(500), nullable=False)
    condition       = db.Column(db.String(20), nullable=False, default='smooth')
    condition_label = db.Column(db.String(100), nullable=False, default='Smooth road')
    condition_tip   = db.Column(db.String(200), nullable=False, default='Good road conditions.')

    def to_dict(self):
        return {
            'id':              self.id,
            'corridor':        self.corridor,
            'name':            self.name,
            'lat':             self.lat,
            'lng':             self.lng,
            'description':     self.description,
            'tags':            self.tags.split(','),
            'labels':          self.labels.split('|'),
            'condition':       self.condition,
            'condition_label': self.condition_label,
            'condition_tip':   self.condition_tip
        }

class Note(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    stop_id    = db.Column(db.Integer, nullable=False)
    traveller  = db.Column(db.String(100), nullable=False)
    note       = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id':         self.id,
            'stop_id':    self.stop_id,
            'traveller':  self.traveller,
            'note':       self.note,
            'created_at': self.created_at
        }

def seed_data():
    stops = [
        # ── DELHI TO MANALI ───────────────────────────────────────────────
        Stop(corridor="delhi-manali", name="Delhi",         lat=28.6139, lng=77.2090, description="Start your journey. Fill fuel, carry cash for toll booths ahead.",                           tags="fuel,safe",            labels="⛽ Fuel Available|🌙 Safe at Night",                condition="smooth",     condition_label="Smooth — NH highway",                    condition_tip="Well maintained city roads and expressway. No issues."),
        Stop(corridor="delhi-manali", name="Murthal",       lat=29.0167, lng=76.9833, description="Famous breakfast stop! Best parathas with butter and curd. Dhabas open 24/7.",              tags="food,safe,fuel",       labels="🍽️ Famous Food Stop|🌙 Safe at Night|⛽ Fuel Available", condition="smooth",  condition_label="Smooth — NH1 expressway",                condition_tip="Excellent road quality. Cruise comfortably."),
        Stop(corridor="delhi-manali", name="Chandigarh",    lat=30.7333, lng=76.7794, description="Last major city. Stock up on everything — fuel, medicines, cash, food.",                    tags="fuel,food,safe",       labels="⛽ Fuel Available|🍽️ Good Food|🌙 Safe at Night",   condition="smooth",     condition_label="Smooth — well maintained city roads",    condition_tip="Good roads through Chandigarh. Easy driving."),
        Stop(corridor="delhi-manali", name="Swarghat",      lat=31.1500, lng=76.8300, description="You've entered Himachal! Beautiful tea stop with mountain views.",                          tags="scenic,food",          labels="🏔️ Scenic Views|🍽️ Tea Stop",                       condition="rough",      condition_label="Rough — hilly roads begin here",         condition_tip="Roads get narrower and windier. Manageable for all vehicles. Drive below 40kmph."),
        Stop(corridor="delhi-manali", name="Bilaspur",      lat=31.3400, lng=76.7600, description="Gobind Sagar Lake visible from road. Good place to stretch and eat.",                       tags="scenic,food,fuel",     labels="🏔️ Lake Views|🍽️ Good Dhabas|⛽ Fuel Available",    condition="rough",      condition_label="Rough — winding mountain road",          condition_tip="Curvy roads along the lake. All vehicles manageable. Take it slow."),
        Stop(corridor="delhi-manali", name="Mandi",         lat=31.7080, lng=76.9320, description="Last proper town before mountain roads get serious. Avoid night drive ahead.",              tags="fuel,food,unsafe",     labels="⛽ Fuel Available|🍽️ Good Food|⚠️ Avoid Night Drive Ahead", condition="rough", condition_label="Rough — mountain terrain starts",       condition_tip="Roads are manageable but get serious after this. All vehicles okay till here."),
        Stop(corridor="delhi-manali", name="Bhuntar",       lat=31.8700, lng=77.1100, description="Network starts getting weak. Inform family before signal drops.",                           tags="no-network,fuel",      labels="📵 Network Gets Weak|⛽ Fuel Available",             condition="rough",      condition_label="Rough — narrow mountain roads",          condition_tip="Gets narrower with sharp turns. Drive carefully. Cars and bikes both manageable."),
        Stop(corridor="delhi-manali", name="Kullu",         lat=31.9579, lng=77.1095, description="Beas River flows alongside. Scenic but curvy. Drive slow.",                                tags="scenic,rough,fuel",    labels="🏔️ Beas River Begins|🛣️ Curvy Roads|⛽ Fuel Available", condition="rough", condition_label="Rough — riverside curves ahead",         condition_tip="Curvy roads alongside Beas river. Beautiful but needs full attention. All vehicles okay."),
        Stop(corridor="delhi-manali", name="Manali",        lat=32.2396, lng=77.1887, description="You made it! Explore Old Manali, Hadimba Temple, Solang Valley nearby.",                   tags="scenic,fuel",          labels="🏔️ Scenic|⛽ Fuel Available",                        condition="rough",      condition_label="Rough — last town before high altitude", condition_tip="Town roads are fine. Roads beyond Manali get very rough. Rest here before continuing."),
        Stop(corridor="delhi-manali", name="Solang Valley", lat=32.3182, lng=77.1553, description="Adventure hub! Paragliding, skiing in winter, zorbing.",                                   tags="scenic",               labels="🏔️ Adventure Sports",                               condition="rough",      condition_label="Rough — steep climb to valley",          condition_tip="Unpaved patches on the way up. Bikes and SUVs preferred. Cars manageable with care."),
        Stop(corridor="delhi-manali", name="Atal Tunnel",   lat=32.3547, lng=77.1723, description="World's longest highway tunnel at 9km, 3100m altitude. Open year round!",                 tags="scenic,safe",          labels="🏔️ Engineering Marvel|🌙 Open Year Round",           condition="smooth",     condition_label="Smooth — tunnel road is well maintained", condition_tip="Inside the tunnel is perfectly smooth. Roads approaching it have some rough patches."),
        Stop(corridor="delhi-manali", name="Rohtang Pass",  lat=32.3713, lng=77.2436, description="Snow covered pass at 3978m. Permit required. Opens late May.",                             tags="scenic,permit,unsafe", labels="🏔️ Scenic at 3978m|📋 Permit Required|⚠️ Closed in Winter", condition="very-rough", condition_label="Very Rough — high altitude pass road",  condition_tip="Loose gravel, rocks, snow patches. Drive below 15kmph. All vehicles can pass but needs skill."),

        # ── DELHI TO LEH ──────────────────────────────────────────────────
        Stop(corridor="delhi-leh", name="Delhi",        lat=28.6139, lng=77.2090, description="Start your journey. Fill fuel, carry cash for toll booths ahead.",                             tags="fuel,safe",             labels="⛽ Fuel Available|🌙 Safe at Night",               condition="smooth",     condition_label="Smooth — NH highway",                      condition_tip="Well maintained city roads. No issues."),
        Stop(corridor="delhi-leh", name="Murthal",      lat=29.0167, lng=76.9833, description="Famous breakfast stop! Best parathas with butter and curd. Dhabas open 24/7.",                tags="food,safe,fuel",        labels="🍽️ Famous Food Stop|🌙 Safe at Night|⛽ Fuel Available", condition="smooth", condition_label="Smooth — NH1 expressway",                condition_tip="Excellent road quality. Cruise comfortably."),
        Stop(corridor="delhi-leh", name="Chandigarh",   lat=30.7333, lng=76.7794, description="Last major city. Stock up on everything — fuel, medicines, cash, food.",                      tags="fuel,food,safe",        labels="⛽ Fuel Available|🍽️ Good Food|🌙 Safe at Night",  condition="smooth",     condition_label="Smooth — well maintained city roads",      condition_tip="Good roads through Chandigarh. Easy driving."),
        Stop(corridor="delhi-leh", name="Mandi",        lat=31.7080, lng=76.9320, description="Last proper town before mountain roads get serious. Avoid night drive ahead.",                tags="fuel,food,unsafe",      labels="⛽ Fuel Available|🍽️ Good Food|⚠️ Avoid Night Drive Ahead", condition="rough", condition_label="Rough — mountain terrain starts",        condition_tip="Roads manageable but get serious after this. Stock up here."),
        Stop(corridor="delhi-leh", name="Kullu",        lat=31.9579, lng=77.1095, description="Beas River flows alongside. Scenic but curvy. Drive slow.",                                   tags="scenic,rough,fuel",     labels="🏔️ Beas River Begins|🛣️ Curvy Roads|⛽ Fuel Available", condition="rough", condition_label="Rough — riverside curves ahead",          condition_tip="Curvy roads alongside Beas river. All vehicles okay with care."),
        Stop(corridor="delhi-leh", name="Manali",       lat=32.2396, lng=77.1887, description="Last major town before Leh. Rest well, stock up on fuel, food, medicines. Long stretch ahead.", tags="scenic,fuel,food",    labels="🏔️ Scenic|⛽ Last Easy Fuel|🍽️ Good Food",         condition="rough",      condition_label="Rough — last comfortable stop",            condition_tip="Town roads fine. REST HERE. Roads ahead are very challenging."),
        Stop(corridor="delhi-leh", name="Rohtang Pass", lat=32.3713, lng=77.2436, description="Snow covered pass at 3978m. Permit required. Opens late May.",                                tags="scenic,permit,unsafe",  labels="🏔️ Scenic at 3978m|📋 Permit Required|⚠️ Closed in Winter", condition="very-rough", condition_label="Very Rough — snow and gravel mix",     condition_tip="Loose gravel, snow patches. Drive below 15kmph. Manageable with care."),
        Stop(corridor="delhi-leh", name="Keylong",      lat=32.5667, lng=76.9833, description="District HQ of Lahaul. Last town with ATM, medical and proper fuel. Stock everything here.",  tags="fuel,food,safe",        labels="⛽ Last ATM & Fuel|🍽️ Good Food|🌙 Safe Town",     condition="rough",      condition_label="Rough — high altitude mountain road",      condition_tip="Roads manageable. Last proper town. Stock up on everything before continuing."),
        Stop(corridor="delhi-leh", name="Jispa",        lat=32.6833, lng=77.0167, description="Beautiful campsite on Bhaga river banks. Network almost gone. Inform family here.",           tags="scenic,no-network",     labels="🏔️ Scenic Campsite|📵 Last Network Point",         condition="rough",      condition_label="Rough — unpaved patches ahead",            condition_tip="Mix of paved and unpaved road. Bikes and SUVs comfortable. Cars need careful driving."),
        Stop(corridor="delhi-leh", name="Baralacha La", lat=32.7833, lng=77.3833, description="High altitude pass at 4890m. Altitude sickness possible. Drive slow, no stopping long.",      tags="scenic,unsafe",         labels="🏔️ Pass at 4890m|⚠️ Altitude Sickness Risk",      condition="very-rough", condition_label="Very Rough — rocky high altitude pass",    condition_tip="Rocky terrain at 4890m. Drive very slow. All vehicles can pass but altitude is the real challenge."),
        Stop(corridor="delhi-leh", name="Sarchu",       lat=32.9167, lng=77.6333, description="HP-Ladakh border camping ground at 4290m. Cold nights even in summer. Carry warm clothes.",   tags="scenic,unsafe",         labels="🏔️ HP-Ladakh Border|⚠️ Very Cold Nights",          condition="very-rough", condition_label="Very Rough — gravel and rocky stretches",  condition_tip="Challenging terrain but passable. The cold and altitude are bigger concerns than road quality."),
        Stop(corridor="delhi-leh", name="Gata Loops",   lat=33.0833, lng=77.6167, description="Famous 21 hairpin bends climbing to Nakee La. Thrilling but scary. No guardrails in sections.", tags="scenic,unsafe,rough", labels="🏔️ 21 Hairpin Bends|⚠️ No Guardrails|🛣️ Rough Patches", condition="very-rough", condition_label="Very Rough — 21 hairpin bends no guardrails", condition_tip="Extremely technical driving. Go one vehicle at a time on bends. Bikes preferred."),
        Stop(corridor="delhi-leh", name="Pang",         lat=33.1667, lng=77.6500, description="Temporary settlement at 4600m. Last fuel and food before Leh. Very limited options.",         tags="fuel,food,unsafe",      labels="⛽ Last Fuel Before Leh|🍽️ Basic Food Only|⚠️ High Altitude", condition="rough", condition_label="Rough — high plateau road",             condition_tip="Flat but rough plateau road. Manageable for all vehicles. Altitude is main challenge here."),
        Stop(corridor="delhi-leh", name="More Plains",  lat=33.3500, lng=77.7167, description="Surreal flat moonscape at 4500m. One of the most unique stretches on earth. No network.",     tags="scenic,no-network",     labels="🏔️ Surreal Moonscape|📵 No Network",               condition="smooth",     condition_label="Smooth — flat plateau highway",            condition_tip="Surprisingly good flat road. Enjoy the moonscape. Winds can be strong."),
        Stop(corridor="delhi-leh", name="Tanglang La",  lat=33.4833, lng=77.7667, description="Second highest motorable pass at 5328m. Extreme altitude. Headache common. Don't stop long.", tags="scenic,unsafe",         labels="🏔️ Pass at 5328m|⚠️ Extreme Altitude",             condition="very-rough", condition_label="Very Rough — extreme altitude pass",       condition_tip="Rocky and uneven at 5328m. Don't stop engine for long. Drive through steadily."),
        Stop(corridor="delhi-leh", name="Leh",          lat=34.1526, lng=77.5771, description="You made it to Leh! Acclimatize for 2 days before exploring. Visit Leh Palace, Pangong Lake.", tags="scenic,fuel,food,safe", labels="🏔️ You Made It!|⛽ Fuel Available|🍽️ Good Food|🌙 Safe City", condition="smooth", condition_label="Smooth — well maintained town roads", condition_tip="Leh town has good roads. Relax — you've earned it!"),

        # ── DELHI TO SHIMLA ───────────────────────────────────────────────
        Stop(corridor="delhi-shimla", name="Delhi",       lat=28.6139, lng=77.2090, description="Start early to avoid city traffic. NH44 to NH48 — good expressway ahead.",                  tags="fuel,safe,food",        labels="⛽ Fuel Available|🌙 Safe|🍽️ Good Food",            condition="smooth",     condition_label="Smooth — NH expressway",                   condition_tip="Well maintained city roads. Start before 7am to beat traffic."),
        Stop(corridor="delhi-shimla", name="Ambala",      lat=30.3782, lng=76.7767, description="Major junction city. Good fuel and food options. NH5 to Shimla begins here.",                tags="fuel,food,safe",        labels="⛽ Fuel Available|🍽️ Good Food|🌙 Safe",            condition="smooth",     condition_label="Smooth — good NH roads",                   condition_tip="Well maintained highway. Easy comfortable driving."),
        Stop(corridor="delhi-shimla", name="Chandigarh",  lat=30.7333, lng=76.7794, description="Last major city before hills. Stock up on everything here.",                                 tags="fuel,food,safe",        labels="⛽ Fuel Available|🍽️ Good Food|🌙 Safe at Night",  condition="smooth",     condition_label="Smooth — well maintained city roads",      condition_tip="Good roads through Chandigarh. Last flat comfortable stretch."),
        Stop(corridor="delhi-shimla", name="Kalka",       lat=30.8388, lng=76.9478, description="Gateway to Shimla. Famous toy train starts here. Roads start climbing from Kalka.",          tags="scenic,food,fuel",      labels="🏔️ Toy Train Station|🍽️ Good Dhabas|⛽ Fuel Available", condition="rough",  condition_label="Rough — mountain roads begin",             condition_tip="Roads get steep and winding from here. All vehicles manageable. Drive below 40kmph."),
        Stop(corridor="delhi-shimla", name="Solan",       lat=30.9045, lng=77.0967, description="Mushroom city of India! Good food and fuel. Scenic stretch begins here.",                    tags="food,fuel,scenic",      labels="🍽️ Famous for Mushrooms|⛽ Fuel Available|🏔️ Scenic", condition="rough",  condition_label="Rough — hilly winding road",               condition_tip="Winding mountain roads but well maintained. All vehicles okay. Enjoy the scenery."),
        Stop(corridor="delhi-shimla", name="Shimla",      lat=31.1048, lng=77.1734, description="Queen of Hills! Mall Road, Christ Church, Jakhu Temple. Parking is a challenge in peak season.", tags="scenic,food,safe",  labels="🏔️ Queen of Hills|🍽️ Famous Mall Road|🌙 Safe City", condition="rough",  condition_label="Rough — steep narrow town roads",          condition_tip="Shimla town roads are very steep and narrow. Park at lower areas and walk or take ropeway. Worth it!"),
        Stop(corridor="delhi-shimla", name="Kufri",       lat=31.0989, lng=77.2647, description="Snow point near Shimla! Horse riding, skiing in winter. 16km from Shimla.",                  tags="scenic,unsafe",         labels="🏔️ Snow Point|⚠️ Slippery in Winter",              condition="rough",      condition_label="Rough — steep climb to Kufri",             condition_tip="Road is steep and narrow. Manageable in good weather. Avoid in heavy snowfall."),
        Stop(corridor="delhi-shimla", name="Chail",       lat=30.9667, lng=77.2000, description="Highest cricket ground in the world! Chail Palace. Peaceful alternative to crowded Shimla.", tags="scenic,safe",           labels="🏔️ Highest Cricket Ground|🌙 Peaceful & Safe",      condition="rough",      condition_label="Rough — narrow forest road",               condition_tip="Narrow but scenic road through dense forest. All vehicles manageable. Drive slow and enjoy."),

        # ── PUNE TO GOA ───────────────────────────────────────────────────
        Stop(corridor="pune-goa", name="Pune",           lat=18.5204, lng=73.8567, description="Start here. Fill up fuel, grab snacks. NH48 begins — smooth expressway ahead.",              tags="fuel,safe,food",            labels="⛽ Fuel Available|🌙 Safe at Night|🍽️ Good Food",  condition="smooth",     condition_label="Smooth — expressway quality",              condition_tip="Excellent NH48 expressway. Cruise at highway speed comfortably."),
        Stop(corridor="pune-goa", name="Satara",         lat=17.6805, lng=74.0183, description="First major stop. Famous for strawberries and Kaas Plateau nearby. Good dhabas.",            tags="food,scenic,fuel",          labels="🍽️ Good Food|🏔️ Scenic Region|⛽ Fuel Available",  condition="smooth",     condition_label="Smooth — NH continues well",               condition_tip="Good road quality. Easy driving. Ghat section starts after this."),
        Stop(corridor="pune-goa", name="Kolhapur",       lat=16.7050, lng=74.2433, description="Famous for Kolhapuri chappal and spicy misal. Stock up on fuel before ghat section.",        tags="food,fuel,safe",            labels="🍽️ Famous Food|⛽ Fuel Available|🌙 Safe at Night", condition="smooth",     condition_label="Smooth — good city roads",                 condition_tip="Good roads through Kolhapur. Roads get ghattier after this."),
        Stop(corridor="pune-goa", name="Amboli Ghat",    lat=15.9583, lng=74.0000, description="Stunning Western Ghats stretch. Fog heavy in monsoon. Drive very slow. Zero visibility possible.", tags="scenic,unsafe,no-network", labels="🏔️ Stunning Ghats|⚠️ Foggy in Monsoon|📵 Weak Network", condition="rough", condition_label="Rough — steep ghat with sharp turns",   condition_tip="Narrow ghat road with sharp hairpins. Manageable for all vehicles. In monsoon fog is the real danger."),
        Stop(corridor="pune-goa", name="Sawantwadi",     lat=15.9043, lng=73.8181, description="Last Maharashtra town. Known for wooden toys. Goa border just ahead.",                       tags="food,fuel,safe",            labels="🍽️ Local Food|⛽ Fuel Available|🌙 Safe Stop",      condition="smooth",     condition_label="Smooth — good roads to Goa border",        condition_tip="Roads improve significantly after the ghats. Easy riding to Goa."),
        Stop(corridor="pune-goa", name="Panaji",         lat=15.4909, lng=73.8278, description="Goa capital. Gorgeous Portuguese architecture, Mandovi river views. You've arrived!",        tags="scenic,food,safe",          labels="🏔️ Scenic City|🍽️ Great Food|🌙 Safe",             condition="smooth",     condition_label="Smooth — well maintained Goa roads",       condition_tip="Goa has good roads. Narrow in old city areas but manageable."),
        Stop(corridor="pune-goa", name="Baga Beach",     lat=15.5552, lng=73.7516, description="Most popular beach stretch. Crowded but vibrant. Watch for rash driving at night.",          tags="scenic,unsafe",             labels="🏔️ Beautiful Beach|⚠️ Careful at Night",           condition="smooth",     condition_label="Smooth — beach roads are fine",            condition_tip="Roads are good but get very crowded. Watch for pedestrians at night."),
        Stop(corridor="pune-goa", name="Colva Beach",    lat=15.2793, lng=73.9121, description="Quieter southern Goa beach. Cleaner, less crowded. Great for bikers who want peace.",        tags="scenic,safe",               labels="🏔️ Scenic & Peaceful|🌙 Safer than North Goa",      condition="smooth",     condition_label="Smooth — quiet beach roads",               condition_tip="Good roads, less traffic. Best riding experience in Goa."),

        # ── MUMBAI TO GOA ─────────────────────────────────────────────────
        Stop(corridor="mumbai-goa", name="Mumbai",        lat=19.0760, lng=72.8777, description="Start from Vashi or Panvel to skip city traffic. NH66 coastal highway begins here.",        tags="fuel,safe,food",            labels="⛽ Fuel Available|🌙 Safe|🍽️ Good Food",            condition="smooth",     condition_label="Smooth — NH66 coastal highway",            condition_tip="Good highway quality. Start early to avoid Mumbai traffic. Panvel is the real starting point."),
        Stop(corridor="mumbai-goa", name="Panvel",         lat=18.9894, lng=73.1175, description="Real start point for most bikers. NH66 begins properly here. Last big city fuel stop.",    tags="fuel,food,safe",            labels="⛽ Fuel Available|🍽️ Good Food|🌙 Safe",            condition="smooth",     condition_label="Smooth — NH66 starts well",                condition_tip="Excellent road quality begins here. Cruise comfortably on the coastal highway."),
        Stop(corridor="mumbai-goa", name="Mahad",          lat=18.0681, lng=73.4177, description="Savitri river crossing. Scenic ghats nearby. Watch for heavy trucks on this stretch.",     tags="food,fuel,scenic",          labels="🍽️ Good Dhabas|⛽ Fuel Available|🏔️ Scenic Ghats",  condition="smooth",     condition_label="Smooth — good NH66",                       condition_tip="Road quality is good. Watch for heavy trucks especially near the river bridge."),
        Stop(corridor="mumbai-goa", name="Chiplun",        lat=17.5333, lng=73.5167, description="Beautiful Vashishti river town. Famous for mangoes. Scenic stretch ahead.",                tags="food,scenic,fuel",          labels="🍽️ Famous Mangoes|🏔️ Scenic River|⛽ Fuel Available", condition="smooth",   condition_label="Smooth — excellent coastal highway",       condition_tip="One of the best stretches of NH66. Smooth road, beautiful scenery. Enjoy the ride."),
        Stop(corridor="mumbai-goa", name="Ratnagiri",      lat=16.9944, lng=73.3000, description="Alphonso mango capital! Ratnadurg Fort nearby. Good overnight stop if needed.",            tags="food,fuel,safe,scenic",     labels="🍽️ Alphonso Mangoes|⛽ Fuel Available|🌙 Safe|🏔️ Fort Views", condition="smooth", condition_label="Smooth — well maintained NH",             condition_tip="Good roads through Ratnagiri. Great place to rest and eat."),
        Stop(corridor="mumbai-goa", name="Vengurla",       lat=15.8593, lng=73.6330, description="Last major Maharashtra town before Goa. Beautiful beaches nearby. Almost there!",          tags="food,fuel,safe,scenic",     labels="🍽️ Good Food|⛽ Fuel Available|🌙 Safe|🏔️ Scenic Beach", condition="smooth", condition_label="Smooth — coastal road continues well",    condition_tip="Road quality remains good. Beautiful coastal views. Last fuel before Goa border."),
        Stop(corridor="mumbai-goa", name="Panaji",         lat=15.4909, lng=73.8278, description="Goa capital! Portuguese architecture, Mandovi river, casino boats. You've arrived!",      tags="scenic,food,safe",          labels="🏔️ Scenic City|🍽️ Great Food|🌙 Safe",             condition="smooth",     condition_label="Smooth — well maintained Goa roads",       condition_tip="Goa roads are good. Enjoy the laid back coastal vibe!"),
        Stop(corridor="mumbai-goa", name="Calangute Beach", lat=15.5440, lng=73.7552, description="King of beaches in North Goa! Most happening beach. Water sports, shacks, nightlife.",   tags="scenic,unsafe",             labels="🏔️ King of Beaches|⚠️ Crowded at Night",           condition="smooth",     condition_label="Smooth — beach roads fine",                condition_tip="Road quality good but extremely crowded in peak season. Watch for drunk drivers at night."),
        Stop(corridor="mumbai-goa", name="Palolem Beach",  lat=15.0100, lng=74.0232, description="Southernmost popular beach. Crescent shaped, calm waters. Quieter than North Goa.",       tags="scenic,safe",               labels="🏔️ Crescent Beach|🌙 Calm & Safe",                  condition="smooth",     condition_label="Smooth — South Goa roads",                 condition_tip="Good roads, less traffic. South Goa is the best for relaxed biking experience."),

        # ── BANGALORE TO COORG ────────────────────────────────────────────
        Stop(corridor="bangalore-coorg", name="Bangalore",   lat=12.9716, lng=77.5946, description="Start from Silk Board or Mysore Road. Heavy traffic till city outskirts. Start early morning.", tags="fuel,safe,food",           labels="⛽ Fuel Available|🌙 Safe|🍽️ Good Food",           condition="smooth",     condition_label="Smooth — city roads heavy traffic",        condition_tip="Roads are good but traffic is heavy. Start before 6am to avoid Bangalore traffic."),
        Stop(corridor="bangalore-coorg", name="Mysore",      lat=12.2958, lng=76.6394, description="Stop at the famous Mysore Palace area. Great idli-dosa breakfast options. NH275 continues.",    tags="food,scenic,fuel",         labels="🍽️ Famous Breakfast|🏔️ Mysore Palace|⛽ Fuel Available", condition="smooth", condition_label="Smooth — excellent NH275",               condition_tip="Very good road quality all the way from Bangalore. Easy comfortable drive."),
        Stop(corridor="bangalore-coorg", name="Hunsur",      lat=12.3003, lng=76.2917, description="Gateway to Coorg region. Last town with full fuel and ATM access before hills.",                tags="fuel,food,safe",           labels="⛽ Last Major Fuel|🍽️ Good Dhabas|🌙 Safe Stop",   condition="smooth",     condition_label="Smooth — roads still good here",           condition_tip="Last stretch of flat good road. Roads get hilly and winding after Hunsur."),
        Stop(corridor="bangalore-coorg", name="Nagarhole",   lat=12.1726, lng=76.1162, description="Nagarhole National Park stretch. Watch for wildlife crossing at dawn/dusk. No overtaking.",     tags="scenic,unsafe",            labels="🏔️ Wildlife Zone|⚠️ Animal Crossing Risk",         condition="smooth",     condition_label="Smooth — forest road drive slow",          condition_tip="Road quality is good but wildlife crossing is real. Drive below 40kmph through forest."),
        Stop(corridor="bangalore-coorg", name="Kushalnagar", lat=12.4584, lng=75.9643, description="Tibetan settlement nearby — Bylakuppe. Great momos! Last ATM before Madikeri.",                 tags="food,fuel,safe",           labels="🍽️ Try Local Momos|⛽ Fuel Available|🌙 Safe",      condition="rough",      condition_label="Rough — hilly roads begin",                condition_tip="Roads get winding after Kushalnagar. Manageable for all vehicles. Beautiful scenery."),
        Stop(corridor="bangalore-coorg", name="Madikeri",    lat=12.4244, lng=75.7382, description="Coorg district HQ. Beautiful misty town. Visit Raja's Seat for sunset. Coffee plantations everywhere.", tags="scenic,food,safe",  labels="🏔️ Misty & Scenic|🍽️ Coorg Coffee|🌙 Safe Town",  condition="rough",      condition_label="Rough — steep winding town roads",         condition_tip="Madikeri town roads are narrow and steep. Manageable but go slow."),
        Stop(corridor="bangalore-coorg", name="Abbey Falls", lat=12.4167, lng=75.7333, description="Beautiful waterfall 8km from Madikeri. Slippery roads in monsoon. Must visit.",                 tags="scenic,unsafe",            labels="🏔️ Stunning Waterfall|⚠️ Slippery in Monsoon",     condition="rough",      condition_label="Rough — narrow forest road to falls",      condition_tip="Narrow road with some unpaved patches. All vehicles okay in dry weather. Slippery in monsoon."),
        Stop(corridor="bangalore-coorg", name="Talacauvery", lat=12.3833, lng=75.4833, description="Origin of river Cauvery. Sacred site. Road gets narrow and steep. No network beyond this point.", tags="scenic,no-network,unsafe", labels="🏔️ Sacred & Scenic|📵 No Network|⚠️ Steep Roads",  condition="very-rough", condition_label="Very Rough — steep narrow climb",          condition_tip="Very narrow road with steep gradient. Small cars and bikes preferred. Large vehicles should avoid."),

        # ── CHENNAI TO OOTY ───────────────────────────────────────────────
        Stop(corridor="chennai-ooty", name="Chennai",      lat=13.0827, lng=80.2707, description="Start from Chennai. NH44 towards Bangalore. Start early to beat city traffic.",            tags="fuel,safe,food",            labels="⛽ Fuel Available|🌙 Safe|🍽️ Good Food",            condition="smooth",     condition_label="Smooth — NH44 expressway",                 condition_tip="Well maintained expressway. Start before 7am to avoid Chennai traffic."),
        Stop(corridor="chennai-ooty", name="Vellore",      lat=12.9165, lng=79.1325, description="Famous for Vellore Fort and CMC Hospital. Good fuel and food stop on NH44.",               tags="food,fuel,safe",            labels="🍽️ Good Food|⛽ Fuel Available|🌙 Safe",            condition="smooth",     condition_label="Smooth — good NH44",                       condition_tip="Excellent road quality. Easy comfortable driving."),
        Stop(corridor="chennai-ooty", name="Krishnagiri",  lat=12.5186, lng=78.2137, description="Mango belt of Tamil Nadu. Famous for Krishnagiri dam and mangoes. Good pit stop.",         tags="food,fuel,scenic",          labels="🍽️ Famous Mangoes|⛽ Fuel Available|🏔️ Scenic Dam",  condition="smooth",     condition_label="Smooth — NH continues well",               condition_tip="Good road quality. Great place to grab mangoes in season."),
        Stop(corridor="chennai-ooty", name="Dharmapuri",   lat=12.1278, lng=78.1580, description="Junction point. Take the route via Hogenakkal or direct to Salem. Waterfalls nearby.",    tags="food,fuel,scenic",          labels="🍽️ Good Dhabas|⛽ Fuel Available|🏔️ Scenic Waterfalls", condition="smooth", condition_label="Smooth — good state highway",              condition_tip="Road quality good. Worth a detour to Hogenakkal waterfalls if time permits."),
        Stop(corridor="chennai-ooty", name="Salem",        lat=11.6643, lng=78.1460, description="Steel city of Tamil Nadu. Good food and fuel. Junction for Ooty via Yercaud ghat.",        tags="food,fuel,safe",            labels="🍽️ Good Food|⛽ Fuel Available|🌙 Safe City",        condition="smooth",     condition_label="Smooth — well maintained city roads",      condition_tip="Good roads through Salem. Stock up before the ghat section begins."),
        Stop(corridor="chennai-ooty", name="Mettupalayam", lat=11.2977, lng=76.9336, description="Foothills of Nilgiris. Toy train to Ooty starts here. Ghat road begins — drive carefully.", tags="scenic,fuel,food",         labels="🏔️ Nilgiris Gateway|⛽ Fuel Available|🍽️ Good Food", condition="rough",   condition_label="Rough — ghat section begins",              condition_tip="Roads get steep and winding from here. All vehicles manageable. Drive below 30kmph on ghats."),
        Stop(corridor="chennai-ooty", name="Coonoor",      lat=11.3530, lng=76.7959, description="Beautiful tea garden town before Ooty. Less crowded than Ooty. Great viewpoints.",         tags="scenic,food,safe",          labels="🏔️ Tea Gardens|🍽️ Good Food|🌙 Safe Town",          condition="rough",      condition_label="Rough — steep mountain roads",             condition_tip="Winding mountain roads but well maintained. All vehicles okay. Beautiful tea estate views."),
        Stop(corridor="chennai-ooty", name="Ooty",         lat=11.4102, lng=76.6950, description="Queen of Hill Stations! Botanical gardens, Ooty lake, tea museum. Very crowded in peak season.", tags="scenic,food,safe",     labels="🏔️ Queen of Hills|🍽️ Famous Nilgiri Tea|🌙 Safe",  condition="rough",      condition_label="Rough — steep narrow town roads",          condition_tip="Ooty town roads are very steep and narrow. Park outside and use local transport. Worth every bit!"),

        # ── HYDERABAD TO HAMPI ────────────────────────────────────────────
        Stop(corridor="hyderabad-hampi", name="Hyderabad",   lat=17.3850, lng=78.4867, description="Start from Hyderabad. NH44 southward. Famous for biryani — eat well before the ride!",  tags="fuel,safe,food",            labels="⛽ Fuel Available|🌙 Safe|🍽️ Famous Biryani",       condition="smooth",     condition_label="Smooth — NH44 expressway",                 condition_tip="Well maintained expressway. Start early to beat Hyderabad traffic."),
        Stop(corridor="hyderabad-hampi", name="Kurnool",      lat=15.8281, lng=78.0373, description="Gateway to Nallamala forest. Tungabhadra river nearby. Good fuel and food stop.",       tags="food,fuel,safe",            labels="🍽️ Good Food|⛽ Fuel Available|🌙 Safe",            condition="smooth",     condition_label="Smooth — good NH roads",                   condition_tip="Good road quality. Easy comfortable drive. Stock up before the forest stretch."),
        Stop(corridor="hyderabad-hampi", name="Nandyal",      lat=15.4786, lng=78.4836, description="Scenic town near Nallamala hills. Watch for wildlife on road at night.",                tags="scenic,unsafe,fuel",        labels="🏔️ Scenic Hills|⚠️ Wildlife at Night|⛽ Fuel Available", condition="smooth", condition_label="Smooth — decent state highway",            condition_tip="Road quality decent. Be careful at night — wildlife crossing common near forest patches."),
        Stop(corridor="hyderabad-hampi", name="Adoni",        lat=15.6270, lng=77.2742, description="Last major town before Hampi. Good fuel stop. Roads get more rural after this.",        tags="fuel,food,safe",            labels="⛽ Fuel Available|🍽️ Good Dhabas|🌙 Safe",          condition="smooth",     condition_label="Smooth — state highway",                   condition_tip="Road quality decent. Last comfortable town before Hampi area."),
        Stop(corridor="hyderabad-hampi", name="Hospet",       lat=15.2689, lng=76.3909, description="Gateway to Hampi. Base town for exploring Hampi ruins. Good hotels and food.",          tags="food,fuel,safe",            labels="🍽️ Good Food|⛽ Fuel Available|🌙 Safe Base Town",   condition="smooth",     condition_label="Smooth — good town roads",                 condition_tip="Good roads in Hospet. Park here and take local transport to Hampi ruins."),
        Stop(corridor="hyderabad-hampi", name="Hampi",         lat=15.3350, lng=76.4600, description="UNESCO World Heritage Site! Ancient Vijayanagara ruins. Boulder landscape is surreal. A must visit for every traveller.", tags="scenic,safe", labels="🏔️ UNESCO Heritage|🌙 Safe to Explore",            condition="rough",      condition_label="Rough — unpaved paths inside ruins",       condition_tip="Roads to Hampi are fine but inside ruins it's unpaved. Bike is the best way to explore. Cars can park outside."),
        Stop(corridor="hyderabad-hampi", name="Tungabhadra Dam", lat=15.2694, lng=76.3345, description="Massive dam on Tungabhadra river. Beautiful evening views. Good picnic spot near Hampi.", tags="scenic,safe",          labels="🏔️ Scenic Dam|🌙 Safe Spot",                        condition="smooth",     condition_label="Smooth — well maintained dam road",        condition_tip="Good roads to the dam. Best visited at sunset. Parking available."),

        # ── MUMBAI TO PUNE ────────────────────────────────────────────────
        Stop(corridor="mumbai-pune", name="Mumbai",          lat=19.0760, lng=72.8777, description="Start from Sion or Eastern Express Highway. NH48 expressway is the fastest route.",      tags="fuel,safe,food",            labels="⛽ Fuel Available|🌙 Safe|🍽️ Good Food",            condition="smooth",     condition_label="Smooth — expressway quality",              condition_tip="Mumbai Pune Expressway is excellent. But very busy on weekends. Start early."),
        Stop(corridor="mumbai-pune", name="Khopoli",         lat=18.7667, lng=73.3500, description="Last exit before the famous Expressway ghats. Good fuel stop. Khopoli has nice waterfalls nearby.", tags="fuel,food,scenic",   labels="⛽ Fuel Available|🍽️ Good Food|🏔️ Scenic Waterfalls", condition="smooth",   condition_label="Smooth — expressway continues",            condition_tip="Well maintained expressway. Last comfortable fuel stop before the ghat section."),
        Stop(corridor="mumbai-pune", name="Khandala",        lat=18.7667, lng=73.3833, description="Famous hill station! Tiger's Leap viewpoint is stunning. Cool weather, misty in monsoon.", tags="scenic,food,safe",        labels="🏔️ Tiger's Leap View|🍽️ Good Food|🌙 Safe",        condition="rough",      condition_label="Rough — ghat section, steep descent",      condition_tip="Expressway ghat section is well maintained but steep. Drive carefully. Beautiful views."),
        Stop(corridor="mumbai-pune", name="Lonavala",        lat=18.7537, lng=73.4068, description="Famous for chikki! Bhushi dam, Pavna lake nearby. Very crowded on weekends.",            tags="food,scenic,safe",          labels="🍽️ Famous Chikki|🏔️ Scenic Lakes|🌙 Safe Town",    condition="smooth",     condition_label="Smooth — well maintained town roads",      condition_tip="Good roads in Lonavala. Extremely crowded on weekends. Avoid peak hours."),
        Stop(corridor="mumbai-pune", name="Talegaon",        lat=18.7333, lng=73.6667, description="Quiet town before Pune. Old NH4 route goes through here. Scenic grape farms.",           tags="food,fuel,scenic",          labels="🍽️ Good Dhabas|⛽ Fuel Available|🏔️ Grape Farms",   condition="smooth",     condition_label="Smooth — good state road",                 condition_tip="Road quality good. Nice stretch through grape farm country. Peaceful drive."),
        Stop(corridor="mumbai-pune", name="Pune",            lat=18.5204, lng=73.8567, description="Oxford of the East! Shaniwar Wada, Aga Khan Palace, amazing food scene. You've arrived!", tags="scenic,food,safe,fuel",    labels="🏔️ Historic City|🍽️ Amazing Food Scene|🌙 Safe|⛽ Fuel Available", condition="smooth", condition_label="Smooth — well maintained city roads", condition_tip="Pune has good roads. Traffic can be heavy in peak hours. Park and explore on foot or metro."),
    ]
    db.session.add_all(stops)
    db.session.commit()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/corridors')
def get_corridors():
    return jsonify([
        { 'id': 'delhi-manali',     'label': 'Delhi → Manali',     'center': [31.0, 77.2],  'zoom': 7 },
        { 'id': 'delhi-leh',        'label': 'Delhi → Leh',        'center': [32.5, 77.5],  'zoom': 6 },
        { 'id': 'delhi-shimla',     'label': 'Delhi → Shimla',     'center': [30.5, 77.0],  'zoom': 8 },
        { 'id': 'pune-goa',         'label': 'Pune → Goa',         'center': [16.8, 74.0],  'zoom': 7 },
        { 'id': 'mumbai-goa',       'label': 'Mumbai → Goa',       'center': [17.5, 73.5],  'zoom': 7 },
        { 'id': 'bangalore-coorg',  'label': 'Bangalore → Coorg',  'center': [12.4, 76.5],  'zoom': 8 },
        { 'id': 'chennai-ooty',     'label': 'Chennai → Ooty',     'center': [12.0, 78.5],  'zoom': 7 },
        { 'id': 'hyderabad-hampi',  'label': 'Hyderabad → Hampi',  'center': [16.0, 77.5],  'zoom': 7 },
        { 'id': 'mumbai-pune',      'label': 'Mumbai → Pune',      'center': [18.8, 73.4],  'zoom': 9 },
    ])

@app.route('/api/stops/<corridor>')
def get_stops(corridor):
    stops = Stop.query.filter_by(corridor=corridor).all()
    return jsonify([s.to_dict() for s in stops])

@app.route('/api/notes/<int:stop_id>')
def get_notes(stop_id):
    notes = Note.query.filter_by(stop_id=stop_id).all()
    return jsonify([n.to_dict() for n in notes])

@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    note = Note(
        stop_id    = data['stop_id'],
        traveller  = data['traveller'],
        note       = data['note'],
        created_at = datetime.now().strftime('%d %b %Y')
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201

@app.route('/api/weather')
def get_weather():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = { 'lat': lat, 'lon': lng, 'appid': WEATHER_API_KEY, 'units': 'metric' }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return jsonify({
            'temp':        round(data['main']['temp']),
            'feels_like':  round(data['main']['feels_like']),
            'description': data['weather'][0]['description'].capitalize(),
            'humidity':    data['main']['humidity'],
            'wind':        round(data['wind']['speed']),
            'icon':        data['weather'][0]['icon']
        })
    except:
        return jsonify({ 'error': 'Weather unavailable' }), 500

@app.route('/admin')
def admin():
    all_notes = Note.query.order_by(Note.id.desc()).all()
    notes_html = ''
    for n in all_notes:
        stop = Stop.query.get(n.stop_id)
        stop_name = stop.name if stop else 'Unknown'
        notes_html += '''
        <tr>
          <td>{}</td>
          <td>{}</td>
          <td>{}</td>
          <td>{}</td>
          <td>{}</td>
          <td><a href="/admin/delete/{}" onclick="return confirm('Delete this note?')"
          style="color:#e74c3c;font-weight:600;text-decoration:none;">Delete</a></td>
        </tr>
        '''.format(n.id, stop_name, n.traveller, n.note, n.created_at, n.id)

    return '''
    <!DOCTYPE html>
    <html>
    <head>
      <title>RoadSoul Admin</title>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Inter', sans-serif; background: #0f0f1a; color: #eee; padding: 30px; }}
        h1 {{ color: #4fc3f7; margin-bottom: 6px; }}
        .subtitle {{ color: #555; font-size: 13px; margin-bottom: 24px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 12px; overflow: hidden; }}
        th {{ background: #1e2a3a; padding: 12px 16px; text-align: left; font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 1px; }}
        td {{ padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #1e2a3a; color: #aaa; vertical-align: top; max-width: 300px; word-wrap: break-word; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #1a2535; }}
        .empty {{ text-align: center; padding: 40px; color: #444; }}
        .stats {{ background: #16213e; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; border: 1px solid #1e2a3a; display: inline-block; }}
        .stats span {{ color: #4fc3f7; font-weight: 700; font-size: 20px; }}
        .back {{ display: inline-block; margin-bottom: 20px; color: #4fc3f7; text-decoration: none; font-size: 13px; }}
        .back:hover {{ text-decoration: underline; }}
      </style>
    </head>
    <body>
      <h1>🛣️ RoadSoul Admin</h1>
      <div class="subtitle">Manage traveller notes</div>
      <a href="/" class="back">← Back to RoadSoul</a>
      <div class="stats">Total Notes: <span>{}</span></div>
      <table>
        <thead>
          <tr><th>ID</th><th>Stop</th><th>Traveller</th><th>Note</th><th>Date</th><th>Action</th></tr>
        </thead>
        <tbody>{}</tbody>
      </table>
      {}
    </body>
    </html>
    '''.format(
        Note.query.count(),
        notes_html if notes_html else '',
        '<div class="empty">No notes yet.</div>' if not notes_html else ''
    )

@app.route('/admin/delete/<int:note_id>')
def delete_note(note_id):
    note = Note.query.get(note_id)
    if note:
        db.session.delete(note)
        db.session.commit()
    return admin()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Stop.query.count() == 0:
            seed_data()
    app.run(debug=True, host='0.0.0.0')