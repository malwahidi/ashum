"""
Complete list of Tadawul (Saudi Exchange) main market stocks.
Format: {ticker: {name, name_ar, sector}}
Ticker format for yfinance: append ".SR" (e.g., "2222.SR" for Aramco)
"""

TADAWUL_STOCKS = {
    # === Energy ===
    "2222": {"name": "Saudi Aramco", "sector": "Energy"},
    "2030": {"name": "SARCO", "sector": "Energy"},
    "2380": {"name": "Petro Rabigh", "sector": "Energy"},
    "4030": {"name": "BAHRI", "sector": "Energy"},
    "2381": {"name": "Arabian Drilling", "sector": "Energy"},
    "2382": {"name": "ADES", "sector": "Energy"},

    # === Materials ===
    "1201": {"name": "Takween", "sector": "Materials"},
    "1202": {"name": "MEPCO", "sector": "Materials"},
    "1210": {"name": "BCI", "sector": "Materials"},
    "1211": {"name": "Maaden", "sector": "Materials"},
    "1301": {"name": "Aslak", "sector": "Materials"},
    "1304": {"name": "Alyamamah Steel", "sector": "Materials"},
    "1320": {"name": "SSP", "sector": "Materials"},
    "2001": {"name": "Chemanol", "sector": "Materials"},
    "2010": {"name": "SABIC", "sector": "Materials"},
    "2020": {"name": "SABIC Agri-Nutrients", "sector": "Materials"},
    "2060": {"name": "Tasnee", "sector": "Materials"},
    "2090": {"name": "NGC", "sector": "Materials"},
    "2150": {"name": "Zoujaj", "sector": "Materials"},
    "2170": {"name": "Alujain", "sector": "Materials"},
    "2180": {"name": "FIPCO", "sector": "Materials"},
    "2200": {"name": "APC", "sector": "Materials"},
    "2210": {"name": "Nama Chemicals", "sector": "Materials"},
    "2220": {"name": "Maadaniyah", "sector": "Materials"},
    "2223": {"name": "Luberef", "sector": "Materials"},
    "2240": {"name": "Senaat", "sector": "Materials"},
    "2250": {"name": "SIIG", "sector": "Materials"},
    "2290": {"name": "Yansab", "sector": "Materials"},
    "2300": {"name": "SPM", "sector": "Materials"},
    "2310": {"name": "SIPCHEM", "sector": "Materials"},
    "2330": {"name": "Advanced", "sector": "Materials"},
    "2350": {"name": "Saudi Kayan", "sector": "Materials"},
    "2360": {"name": "SVCP", "sector": "Materials"},
    "1321": {"name": "East Pipes", "sector": "Materials"},
    "1322": {"name": "Amak", "sector": "Materials"},
    "1323": {"name": "UCIC", "sector": "Materials"},
    "1324": {"name": "Saleh Alrashed", "sector": "Materials"},

    # === Cement ===
    "3001": {"name": "Yamama Cement", "sector": "Cement"},
    "3002": {"name": "Najran Cement", "sector": "Cement"},
    "3003": {"name": "City Cement", "sector": "Cement"},
    "3004": {"name": "Northern Cement", "sector": "Cement"},
    "3005": {"name": "Umm Al Qura Cement", "sector": "Cement"},
    "3007": {"name": "Oasis", "sector": "Cement"},
    "3008": {"name": "Alkathiri", "sector": "Cement"},
    "3010": {"name": "Arabian Cement", "sector": "Cement"},
    "3020": {"name": "Yamamah Cement", "sector": "Cement"},
    "3030": {"name": "Saudi Cement", "sector": "Cement"},
    "3040": {"name": "Qassim Cement", "sector": "Cement"},
    "3050": {"name": "Southern Cement", "sector": "Cement"},
    "3060": {"name": "Yanbu Cement", "sector": "Cement"},
    "3080": {"name": "Eastern Cement", "sector": "Cement"},
    "3090": {"name": "Tabuk Cement", "sector": "Cement"},
    "3091": {"name": "Hail Cement", "sector": "Cement"},
    "3092": {"name": "Jouf Cement", "sector": "Cement"},

    # === Capital Goods ===
    "1212": {"name": "Astra Industrial", "sector": "Capital Goods"},
    "1302": {"name": "Bawan", "sector": "Capital Goods"},
    "1303": {"name": "EIC", "sector": "Capital Goods"},
    "2040": {"name": "Saudi Ceramics", "sector": "Capital Goods"},
    "2110": {"name": "Saudi Cable", "sector": "Capital Goods"},
    "2160": {"name": "Amiantit", "sector": "Capital Goods"},
    "2320": {"name": "Albabtain", "sector": "Capital Goods"},
    "2370": {"name": "MESC", "sector": "Capital Goods"},
    "4110": {"name": "Saudi Industrial", "sector": "Capital Goods"},
    "4140": {"name": "SIECO", "sector": "Capital Goods"},
    "4141": {"name": "Al-Omran", "sector": "Capital Goods"},
    "4142": {"name": "Alhassan Shaker", "sector": "Capital Goods"},
    "4143": {"name": "Zamil", "sector": "Capital Goods"},
    "4144": {"name": "Tabuk Agriculture", "sector": "Capital Goods"},
    "4145": {"name": "Wadi Aldawaser", "sector": "Capital Goods"},
    "4146": {"name": "RAWEC", "sector": "Capital Goods"},
    "4148": {"name": "DUR Hospitality", "sector": "Capital Goods"},

    # === Transportation ===
    "4031": {"name": "SGS", "sector": "Transportation"},
    "4040": {"name": "SAPTCO", "sector": "Transportation"},
    "4260": {"name": "Budget Saudi", "sector": "Transportation"},
    "4261": {"name": "Theeb Rent a Car", "sector": "Transportation"},
    "4262": {"name": "Lumi Rental", "sector": "Transportation"},
    "4263": {"name": "SAL", "sector": "Transportation"},

    # === Consumer Services ===
    "1810": {"name": "Seera", "sector": "Consumer Services"},
    "1820": {"name": "Baan", "sector": "Consumer Services"},
    "1830": {"name": "Leejam Sports", "sector": "Consumer Services"},
    "1831": {"name": "MIS", "sector": "Consumer Services"},
    "4170": {"name": "TECO", "sector": "Consumer Services"},
    "4290": {"name": "Alhokair", "sector": "Consumer Services"},
    "4291": {"name": "SELA", "sector": "Consumer Services"},
    "6002": {"name": "Herfy", "sector": "Consumer Services"},
    "6004": {"name": "Catrion", "sector": "Consumer Services"},
    "6012": {"name": "Raydan Food", "sector": "Consumer Services"},
    "6013": {"name": "DIR", "sector": "Consumer Services"},
    "6015": {"name": "THIMAR", "sector": "Consumer Services"},
    "6020": {"name": "JAHEZ", "sector": "Consumer Services"},

    # === Media & Entertainment ===
    "4070": {"name": "TAPRCO", "sector": "Media"},
    "4071": {"name": "AlArabia", "sector": "Media"},
    "4072": {"name": "MBC Group", "sector": "Media"},
    "4210": {"name": "SRMG", "sector": "Media"},

    # === Retail ===
    "4001": {"name": "A.Othaim Market", "sector": "Retail"},
    "4003": {"name": "Extra", "sector": "Retail"},
    "4006": {"name": "Farm Superstores", "sector": "Retail"},
    "4050": {"name": "SACO", "sector": "Retail"},
    "4051": {"name": "BinDawood", "sector": "Retail"},
    "4061": {"name": "Anaam Holding", "sector": "Retail"},
    "4160": {"name": "Thamarat", "sector": "Retail"},
    "4161": {"name": "Bindawood", "sector": "Retail"},
    "4162": {"name": "AlDawaa", "sector": "Retail"},
    "4164": {"name": "Nahdi Medical", "sector": "Retail"},
    "4190": {"name": "Jarir", "sector": "Retail"},
    "4191": {"name": "Alhokair Fashion", "sector": "Retail"},
    "4192": {"name": "Alsaif Gallery", "sector": "Retail"},
    "4200": {"name": "Aldrees", "sector": "Retail"},

    # === Food & Beverages ===
    "2050": {"name": "Savola Group", "sector": "Food & Beverages"},
    "2100": {"name": "Wafrah", "sector": "Food & Beverages"},
    "2270": {"name": "Sadafco", "sector": "Food & Beverages"},
    "2280": {"name": "Almarai", "sector": "Food & Beverages"},
    "2281": {"name": "Tanmiah Food", "sector": "Food & Beverages"},
    "2282": {"name": "Naqi Water", "sector": "Food & Beverages"},
    "2283": {"name": "SFDA", "sector": "Food & Beverages"},
    "6001": {"name": "HB", "sector": "Food & Beverages"},
    "6010": {"name": "NADEC", "sector": "Food & Beverages"},
    "6040": {"name": "Tabuk Agriculture", "sector": "Food & Beverages"},
    "6050": {"name": "SADAFCO", "sector": "Food & Beverages"},
    "6060": {"name": "Sharqiyah Development", "sector": "Food & Beverages"},
    "6070": {"name": "AlJouf Agriculture", "sector": "Food & Beverages"},
    "6090": {"name": "JADWA REIT", "sector": "Food & Beverages"},
    "4080": {"name": "Sinad Holding", "sector": "Food & Beverages"},

    # === Healthcare ===
    "4002": {"name": "Mouwasat", "sector": "Healthcare"},
    "4004": {"name": "Dallah Healthcare", "sector": "Healthcare"},
    "4005": {"name": "Care", "sector": "Healthcare"},
    "4007": {"name": "Al Hammadi", "sector": "Healthcare"},
    "4009": {"name": "SMPC", "sector": "Healthcare"},
    "4013": {"name": "Sulaiman Al-Habib", "sector": "Healthcare"},
    "4014": {"name": "KAYAN Medical", "sector": "Healthcare"},
    "2140": {"name": "Ayyan", "sector": "Healthcare"},

    # === Pharma ===
    "2070": {"name": "SPIMACO", "sector": "Pharma"},
    "4015": {"name": "Avalon Pharma", "sector": "Pharma"},

    # === Banks ===
    "1010": {"name": "RIBL", "sector": "Banks"},
    "1020": {"name": "BJAZ", "sector": "Banks"},
    "1030": {"name": "SAIB", "sector": "Banks"},
    "1050": {"name": "BSF", "sector": "Banks"},
    "1060": {"name": "SAB", "sector": "Banks"},
    "1080": {"name": "ANB", "sector": "Banks"},
    "1120": {"name": "Al Rajhi Bank", "sector": "Banks"},
    "1140": {"name": "Albilad", "sector": "Banks"},
    "1150": {"name": "Alinma", "sector": "Banks"},
    "1180": {"name": "SNB", "sector": "Banks"},

    # === Financial Services ===
    "1111": {"name": "Tadawul Group", "sector": "Financial Services"},
    "2120": {"name": "SAIC", "sector": "Financial Services"},
    "4081": {"name": "Alamar Foods", "sector": "Financial Services"},
    "4082": {"name": "Rasan", "sector": "Financial Services"},
    "4130": {"name": "Saudi Darb", "sector": "Financial Services"},
    "4280": {"name": "Kingdom Holding", "sector": "Financial Services"},

    # === Insurance ===
    "8010": {"name": "Tawuniya", "sector": "Insurance"},
    "8012": {"name": "Jazira Takaful", "sector": "Insurance"},
    "8020": {"name": "Malath Insurance", "sector": "Insurance"},
    "8030": {"name": "Medgulf", "sector": "Insurance"},
    "8040": {"name": "AICC", "sector": "Insurance"},
    "8050": {"name": "Salama", "sector": "Insurance"},
    "8060": {"name": "Walaa", "sector": "Insurance"},
    "8070": {"name": "Arabian Shield", "sector": "Insurance"},
    "8080": {"name": "AXA Insurance", "sector": "Insurance"},
    "8100": {"name": "SAAB Takaful", "sector": "Insurance"},
    "8120": {"name": "Gulf Union Alahlia", "sector": "Insurance"},
    "8150": {"name": "ACIG", "sector": "Insurance"},
    "8160": {"name": "Rasan Insurance", "sector": "Insurance"},
    "8170": {"name": "Alrajhi Takaful", "sector": "Insurance"},
    "8180": {"name": "Liva", "sector": "Insurance"},
    "8190": {"name": "Mutakamela", "sector": "Insurance"},
    "8200": {"name": "Bupa Arabia", "sector": "Insurance"},
    "8210": {"name": "Alsagr Insurance", "sector": "Insurance"},
    "8230": {"name": "Aletihad Takaful", "sector": "Insurance"},
    "8240": {"name": "SAICO", "sector": "Insurance"},
    "8250": {"name": "GIG", "sector": "Insurance"},
    "8260": {"name": "Gulf General", "sector": "Insurance"},
    "8270": {"name": "Buruj", "sector": "Insurance"},
    "8280": {"name": "Wataniya", "sector": "Insurance"},
    "8300": {"name": "Amana Insurance", "sector": "Insurance"},
    "8310": {"name": "Chubb Arabia", "sector": "Insurance"},
    "8311": {"name": "Enaya", "sector": "Insurance"},
    "8312": {"name": "Saudi RE", "sector": "Insurance"},
    "8313": {"name": "Rasan IT", "sector": "Insurance"},

    # === Telecom ===
    "7010": {"name": "STC", "sector": "Telecom"},
    "7020": {"name": "Etihad Etisalat (Mobily)", "sector": "Telecom"},
    "7030": {"name": "Zain KSA", "sector": "Telecom"},
    "7040": {"name": "Go Telecom", "sector": "Telecom"},

    # === Utilities ===
    "2080": {"name": "GASCO", "sector": "Utilities"},
    "2081": {"name": "AWPT", "sector": "Utilities"},
    "2082": {"name": "ACWA Power", "sector": "Utilities"},
    "2083": {"name": "Marafiq", "sector": "Utilities"},
    "2084": {"name": "Miahona", "sector": "Utilities"},
    "5110": {"name": "Saudi Electricity", "sector": "Utilities"},

    # === Real Estate ===
    "4020": {"name": "Alandalus", "sector": "Real Estate"},
    "4150": {"name": "Emaar Economic City", "sector": "Real Estate"},
    "4220": {"name": "Arriyadh Development", "sector": "Real Estate"},
    "4230": {"name": "Red Sea International", "sector": "Real Estate"},
    "4240": {"name": "FAWAZ", "sector": "Real Estate"},
    "4250": {"name": "Jabal Omar", "sector": "Real Estate"},
    "4300": {"name": "Dar Al Arkan", "sector": "Real Estate"},
    "4310": {"name": "Knowledge Economic City", "sector": "Real Estate"},
    "4320": {"name": "AlAndalus", "sector": "Real Estate"},
    "4321": {"name": "Retal Urban", "sector": "Real Estate"},
    "4322": {"name": "Cenomi Centers", "sector": "Real Estate"},
    "4323": {"name": "Sumou Real Estate", "sector": "Real Estate"},

    # === REITs ===
    "4330": {"name": "Riyad REIT", "sector": "REITs"},
    "4331": {"name": "Aljazira REIT", "sector": "REITs"},
    "4332": {"name": "JADWA REIT Saudi", "sector": "REITs"},
    "4333": {"name": "Taleem REIT", "sector": "REITs"},
    "4334": {"name": "Almaather REIT", "sector": "REITs"},
    "4335": {"name": "Musharaka REIT", "sector": "REITs"},
    "4336": {"name": "Mulkia REIT", "sector": "REITs"},
    "4337": {"name": "Derayah REIT", "sector": "REITs"},
    "4338": {"name": "Alahli REIT 1", "sector": "REITs"},
    "4339": {"name": "Bonyan REIT", "sector": "REITs"},
    "4340": {"name": "Alnmaa REIT", "sector": "REITs"},
    "4342": {"name": "Alinma Retail REIT", "sector": "REITs"},
    "4344": {"name": "SEDCO Capital REIT", "sector": "REITs"},
    "4345": {"name": "Swicorp Wabel REIT", "sector": "REITs"},
    "4346": {"name": "Alkhabeer REIT", "sector": "REITs"},
    "4347": {"name": "Alrajhi REIT", "sector": "REITs"},
    "4348": {"name": "Himmah REIT", "sector": "REITs"},
    "4349": {"name": "Alinma Hospitality REIT", "sector": "REITs"},
    "4350": {"name": "Saudi Fransi Capital REIT", "sector": "REITs"},

    # === Software & IT ===
    "7200": {"name": "Elm", "sector": "Technology"},
    "7201": {"name": "Alandalus IT", "sector": "Technology"},
    "7202": {"name": "Thiqah", "sector": "Technology"},
    "7203": {"name": "Bayanat", "sector": "Technology"},
    "7204": {"name": "Tiqniyat", "sector": "Technology"},

    # === Consumer Durables ===
    "1213": {"name": "Naseej", "sector": "Consumer Durables"},
    "2130": {"name": "SIDC", "sector": "Consumer Durables"},
    "2340": {"name": "Artex", "sector": "Consumer Durables"},
    "4011": {"name": "Lazurde", "sector": "Consumer Durables"},
    "4180": {"name": "Fitaihi", "sector": "Consumer Durables"},
    "4165": {"name": "Almajed Oud", "sector": "Consumer Durables"},

    # === Commercial Services ===
    "4270": {"name": "SPPC", "sector": "Commercial Services"},
    "1832": {"name": "Thob Al Aseel", "sector": "Commercial Services"},
    "1833": {"name": "Alkhaleej Training", "sector": "Commercial Services"},
}

# TASI Index
TASI_INDEX = "^TASI.SR"

# === الأسهم النقية - قائمة العصيمي (Al-Osaimi Pure Stocks) ===
# Source: Argaam.com Sharia Compliant Companies - Dr. Mohammed Al-Osaimi
NAQI_LAST_UPDATED = "2026-04-12"  # Update this date when list is refreshed
NAQI_UPDATE_DAYS = 90  # Remind after 90 days
NAQI_TICKERS = {
    # Banks
    "1120", "1140", "1020",
    # Petrochemicals
    "2170", "2210", "2010", "2020", "2250", "2290", "2310", "2350", "2001", "2330",
    # Cement
    "3010", "3080", "3040", "3030", "3090", "3020", "3091", "3004", "3002", "3003",
    # Oil & Gas / Energy
    "4200", "2080", "4050", "2222", "2381", "2223", "2030",
    # Glass / Industrial
    "2150", "4145", "4144",
    # Trade & Retail
    "4003", "1214", "4240", "4001", "4160", "4180", "4190", "4006", "4163", "4011",
    "4008", "4051", "4191", "4012", "4161", "4192", "4164", "4193", "4165",
    # Pharma & Healthcare
    "4016", "4015", "2230", "2070", "1212", "4017", "4013", "4009", "4007", "4018",
    "4019", "4005", "4004", "4002",
    # Education
    "4290", "4292", "4291",
    # Food & Beverages / Agriculture
    "4162", "6013", "6012", "6004", "2287", "2284", "6015", "2283", "6014", "2281",
    "2285", "2286", "6016", "2288", "2282", "6002", "6001", "2270", "2050", "2280",
    "2100", "6010", "6020", "6040", "6050", "6060", "6070", "6090", "4061",
    # Multi-Sector / Industrial
    "4140", "4080", "4130", "2120", "2140", "1832",
    # Energy & Utilities
    "2082", "2083", "4146", "2081", "5110",
    # Insurance
    "8010", "8190", "8050", "8180", "8230", "8150", "8210", "8070", "8200", "8120",
    "8020", "8170", "8060", "8030", "8260", "8160", "8250", "8240", "8012", "8300", "8311",
    # Manufacturing / Materials
    "1302", "1201", "1301", "1320", "2360", "1213", "2320", "2340", "1210", "2370",
    "2300", "2090", "2160", "2110", "2040", "2180", "2200", "2220", "2130", "2240",
    "4143", "4194", "1321", "4148", "1202", "1304", "4142", "1303", "3008", "4141",
    "1323", "3007",
    # Mining
    "1322", "1211",
    # REITs
    "4349", "4335", "4336", "4337", "4338", "4344", "4339", "4340", "4345", "4342",
    "4346", "4347", "4348", "4331", "4330", "4333", "4332",
    # Real Estate
    "4321", "4325", "4320", "4324", "4322", "4323", "4310", "4220", "4230", "4090",
    "4300", "4250", "4150", "4020", "4100",
    # Transportation
    "4110", "4040", "4030", "2190", "4260", "4262", "4031", "4261",
    # Media
    "4071", "4210", "4270", "4070",
    # Hotels & Tourism
    "4170", "1810", "1820",
    # Telecom
    "7010", "7020", "7040",
    # IT / Technology
    "7202", "7200", "7201", "7204", "7211", "7203", "8313",
    # HR Services
    "1833", "1834", "1835", "1831",
}


# Arabic company names (source: Argaam.com)
ARABIC_NAMES = {
    "1010": "الرياض",
    "1020": "الجزيرة",
    "1030": "الإستثمار",
    "1050": "بي اس اف",
    "1060": "الأول",
    "1080": "العربي",
    "1111": "مجموعة تداول",
    "1120": "الراجحي",
    "1140": "البلاد",
    "1150": "الإنماء",
    "1180": "الأهلي",
    "1182": "أملاك",
    "1183": "سهل",
    "1201": "تكوين",
    "1202": "مبكو",
    "1210": "بي سي آي",
    "1211": "معادن",
    "1212": "أسترا الصناعية",
    "1213": "نسيج",
    "1214": "شاكر",
    "1301": "أسلاك",
    "1302": "بوان",
    "1303": "الصناعات الكهربائية",
    "1304": "اليمامة للحديد",
    "1320": "أنابيب السعودية",
    "1321": "أنابيب الشرق",
    "1322": "أماك",
    "1323": "يو سي آي سي",
    "1324": "صالح الراشد",
    "1810": "سيرا",
    "1820": "بان",
    "1830": "لجام للرياضة",
    "1831": "مهارة",
    "1832": "صدر",
    "1833": "الموارد",
    "1834": "سماسكو",
    "1835": "تمكين",
    "2001": "كيمانول",
    "2010": "سابك",
    "2020": "سابك للمغذيات الزراعية",
    "2030": "المصافي",
    "2040": "الخزف السعودي",
    "2050": "مجموعة صافولا",
    "2060": "التصنيع",
    "2070": "الدوائية",
    "2080": "الغاز",
    "2081": "الخريف",
    "2082": "أكوا",
    "2083": "مرافق",
    "2084": "مياهنا",
    "2090": "جبسكو",
    "2100": "وفرة",
    "2110": "الكابلات السعودية",
    "2120": "متطورة",
    "2130": "صدق",
    "2140": "أيان",
    "2150": "زجاج",
    "2160": "أميانتيت",
    "2170": "اللجين",
    "2180": "فيبكو",
    "2190": "سيسكو القابضة",
    "2200": "أنابيب",
    "2210": "نماء للكيماويات",
    "2220": "معدنية",
    "2222": "أرامكو السعودية",
    "2223": "لوبريف",
    "2230": "الكيميائية",
    "2240": "صناعات",
    "2250": "المجموعة السعودية",
    "2270": "سدافكو",
    "2280": "المراعي",
    "2281": "تنمية",
    "2282": "نقي",
    "2283": "المطاحن الأولى",
    "2284": "المطاحن الحديثة",
    "2285": "المطاحن العربية",
    "2286": "المطاحن الرابعة",
    "2287": "إنتاج",
    "2288": "نفوذ",
    "2290": "ينساب",
    "2300": "صناعة الورق",
    "2310": "سبكيم العالمية",
    "2320": "البابطين",
    "2330": "المتقدمة",
    "2340": "ارتيكس",
    "2350": "كيان السعودية",
    "2360": "الفخارية",
    "2370": "مسك",
    "2380": "بترو رابغ",
    "2381": "الحفر العربية",
    "2382": "أديس",
    "3002": "أسمنت نجران",
    "3003": "أسمنت المدينة",
    "3004": "أسمنت الشمالية",
    "3005": "أسمنت ام القرى",
    "3007": "الواحة",
    "3008": "الكثيري",
    "3010": "أسمنت العربية",
    "3020": "أسمنت اليمامة",
    "3030": "أسمنت السعودية",
    "3040": "أسمنت القصيم",
    "3050": "أسمنت الجنوب",
    "3060": "أسمنت ينبع",
    "3080": "أسمنت الشرقية",
    "3090": "أسمنت تبوك",
    "3091": "أسمنت الجوف",
    "3092": "أسمنت الرياض",
    "4001": "أسواق ع العثيم",
    "4002": "المواساة",
    "4003": "إكسترا",
    "4004": "دله الصحية",
    "4005": "رعاية",
    "4006": "أسواق المزرعة",
    "4007": "الحمادي",
    "4008": "ساكو",
    "4009": "السعودي الألماني الصحية",
    "4011": "لازوردي",
    "4012": "الأصيل",
    "4013": "سليمان الحبيب",
    "4014": "دار المعدات",
    "4015": "جمجوم فارما",
    "4016": "أفالون فارما",
    "4017": "فقيه الطبية",
    "4018": "الموسى",
    "4019": "اس ام سي للرعاية الصحية",
    "4020": "العقارية",
    "4021": "المركز الكندي الطبي",
    "4030": "البحري",
    "4031": "الخدمات الأرضية",
    "4040": "سابتكو",
    "4050": "ساسكو",
    "4051": "باعظيم",
    "4061": "أنعام القابضة",
    "4070": "تهامة",
    "4071": "العربية",
    "4072": "مجموعة إم بي سي",
    "4080": "سناد القابضة",
    "4081": "النايفات",
    "4083": "تسهيل",
    "4084": "دراية",
    "4090": "طيبة",
    "4100": "مكة",
    "4110": "باتك",
    "4130": "درب السعودية",
    "4140": "صادرات",
    "4141": "العمران",
    "4142": "كابلات الرياض",
    "4143": "تالكو",
    "4144": "رؤوم",
    "4145": "أو جي سي",
    "4146": "جاز",
    "4147": "سي جي إس",
    "4148": "الوسائل الصناعية",
    "4150": "التعمير",
    "4160": "ثمار",
    "4161": "بن داود",
    "4162": "المنجم",
    "4163": "الدواء",
    "4164": "النهدي",
    "4165": "الماجد للعود",
    "4170": "شمس",
    "4180": "مجموعة فتيحي",
    "4190": "جرير",
    "4191": "أبو معطي",
    "4192": "السيف غاليري",
    "4193": "نايس ون",
    "4194": "محطة البناء",
    "4200": "الدريس",
    "4210": "الأبحاث والإعلام",
    "4220": "إعمار",
    "4230": "البحر الأحمر",
    "4240": "سينومي ريتيل",
    "4250": "جبل عمر",
    "4260": "بدجت السعودية",
    "4261": "ذيب",
    "4262": "لومي",
    "4263": "سال",
    "4264": "طيران ناس",
    "4265": "شري",
    "4270": "طباعة وتغليف",
    "4280": "المملكة",
    "4290": "الخليج للتدريب",
    "4291": "الوطنية للتعليم",
    "4292": "عطاء",
    "4300": "دار الأركان",
    "4310": "مدينة المعرفة",
    "4320": "الأندلس",
    "4321": "سينومي سنترز",
    "4322": "رتال",
    "4323": "سمو",
    "4324": "بنان",
    "4325": "مسار",
    "4326": "الماجدية",
    "4327": "الرمز",
    "4330": "الرياض ريت",
    "4331": "الجزيرة ريت",
    "4332": "جدوى ريت الحرمين",
    "4333": "تعليم ريت",
    "4334": "المعذر ريت",
    "4335": "مشاركة ريت",
    "4336": "ملكية ريت",
    "4337": "العزيزية ريت",
    "4338": "الأهلي ريت 1",
    "4339": "دراية ريت",
    "4340": "الراجحي ريت",
    "4342": "جدوى ريت السعودية",
    "4344": "سدكو كابيتال ريت",
    "4345": "الإنماء ريت للتجزئة",
    "4346": "ميفك ريت",
    "4347": "بنيان ريت",
    "4348": "الخبير ريت",
    "4349": "الإنماء ريت الفندقي",
    "4350": "الاستثمار ريت",
    "5110": "السعودية للطاقة",
    "6001": "حلواني إخوان",
    "6002": "هرفي للأغذية",
    "6004": "كاتريون",
    "6010": "نادك",
    "6012": "ريدان",
    "6013": "التطويرية الغذائية",
    "6014": "الآمار",
    "6015": "أمريكانا",
    "6016": "برغرايززر",
    "6017": "جاهز",
    "6018": "الأندية للرياضة",
    "6019": "المسار الشامل",
    "6020": "جاكو",
    "6040": "تبوك الزراعية",
    "6050": "الأسماك",
    "6060": "الشرقية للتنمية",
    "6070": "الجوف ",
    "6090": "جازادكو",
    "7010": "اس تي سي",
    "7020": "إتحاد إتصالات",
    "7030": "زين السعودية",
    "7040": "قو للإتصالات",
    "7200": "ام آي اس",
    "7201": "بحر العرب",
    "7202": "سلوشنز",
    "7203": "علم",
    "7204": "توبي",
    "7211": "عزم",
    "8010": "التعاونية",
    "8012": "جزيرة تكافل",
    "8020": "ملاذ للتأمين",
    "8030": "ميدغلف للتأمين",
    "8040": "متكاملة",
    "8050": "سلامة",
    "8060": "ولاء",
    "8070": "الدرع العربي",
    "8100": "سايكو",
    "8120": "إتحاد الخليج الأهلية",
    "8150": "أسيج",
    "8160": "التأمين العربية",
    "8170": "الاتحاد",
    "8180": "الصقر للتأمين",
    "8190": "المتحدة للتأمين",
    "8200": "الإعادة السعودية",
    "8210": "بوبا العربية",
    "8230": "تكافل الراجحي",
    "8240": "تْشب",
    "8250": "جي آي جي",
    "8260": "الخليجية العامة",
    "8280": "ليفا",
    "8300": "الوطنية",
    "8310": "أمانة للتأمين",
    "8311": "عناية  ",
    "8313": "رسن",
    "9300": "الواحة ريت",
    "9510": "الوطنية للبناء والتسويق",
    "9513": "حديد وطني",
    "9514": "الناقول",
    "9515": "فش فاش",
    "9517": "موبي للصناعة",
    "9521": "إنمار",
    "9522": "الحاسوب",
    "9523": "جروب فايف",
    "9524": "آيكتك",
    "9527": "ألف ميم ياء",
    "9530": "طبية",
    "9532": "مياه الجوف",
    "9533": "المركز الآلي",
    "9535": "لدن",
    "9536": "فاديكو",
    "9537": "أمواج الدولية",
    "9539": "أقاسيم",
    "9540": "تدوير",
    "9541": "أكاديمية التعلم",
    "9542": "كير",
    "9543": "نت وركرس",
    "9544": "الرعاية المستقبلية",
    "9545": "الدولية",
    "9546": "نبع الصحة",
    "9547": "رواسي",
    "9548": "ابيكو",
    "9549": "البابطين الغذائية",
    "9550": "شور",
    "9552": "قمة السعودية",
    "9553": "ملان",
    "9555": "لين الخير",
    "9557": "إدارات",
    "9558": "القمم",
    "9559": "بلدي",
    "9560": "وجا",
    "9561": "نولجنت",
    "9562": "بوابة الأطعمة",
    "9563": "بناء",
    "9564": "آفاق الغذاء",
    "9565": "معيار",
    "9566": "الصناعات الجيرية",
    "9567": "غذاء السلطان",
    "9568": "ميار",
    "9569": "آل منيف",
    "9570": "تام التنموية",
    "9571": "مناوله",
    "9572": "الرازي",
    "9574": "بروميديكس",
    "9575": "ماربل ديزاين",
    "9576": "منزل الورق",
    "9577": "دار المركبة",
    "9578": "مصاعد أطلس",
    "9579": "البخور الذكي",
    "9580": "الراشد للصناعة",
    "9581": "كلين لايف",
    "9583": "المتحدة للتعدين",
    "9584": "ريال",
    "9585": "ملكية",
    "9586": "أصول وبخيت",
    "9587": "لانا",
    "9588": "حديد الرياض",
    "9589": "فاد",
    "9590": "أرماح",
    "9591": "فيو",
    "9592": "المجتمع الطبية",
    "9593": "عبر الخليج",
    "9594": "المداواة",
    "9595": "وسم",
    "9596": "كوارا",
    "9597": "الليف",
    "9598": "المحافظة للتعليم",
    "9599": "طاقات",
    "9600": "كومل",
    "9601": "الرشيد",
    "9602": "يقين",
    "9603": "الأفق التعليمية",
    "9604": "ميرال",
    "9605": "نفط الشرق",
    "9606": "ثروة",
    "9607": "عسق",
    "9608": "الأشغال الميسرة",
    "9609": "بترول ناس",
    "9610": "الجادة الأولى",
    "9611": "المتحدة للزجاج المسطح",
    "9612": "مياه سما",
    "9613": "شلفا",
    "9614": "نقاوة",
    "9615": "مفيد",
    "9616": "جنى",
    "9617": "ارابيكا ستار",
    "9618": "الفاخرة",
    "9619": "الأعمال المتعددة",
    "9620": "بلسم الطبية",
    "9621": "دي آر سي",
    "9622": "شموع الماضي",
    "9623": "مصنع البتال",
    "9624": "الشهيلي المعدنية",
    "9625": "إتمام",
    "9626": "سمايل كير",
    "9627": "طوارئيات",
    "9628": "لمسات",
    "9630": "ريشيو",
    "9631": "هضاب الخليج",
    "9632": "رؤية المستقبل",
    "9633": "آلات الصيانة",
    "9634": "أدير",
    "9635": "دخون",
    "9636": "الخزامى",
    "9637": "الحلول المتسارعة",
    "9639": "أنماط",
    "9640": "أساس مكين",
    "9641": "هوية",
    "9642": "تايم",
    "9644": "ناف",
    "9645": "ساين وورلد",
    "9647": "وجد الحياة",
    "9648": "حمد بن سعيدان العقارية",
    "9649": "جمجوم فاشن",
    "9650": "ساحة المجد",
    "9651": "التويجري",
    "9653": "خالد ظافر وإخوانه",
}


def refresh_arabic_names():
    """
    Fetch latest Arabic company names from Argaam.com.
    Updates ARABIC_NAMES dict with any new companies.
    Falls back to hardcoded names if Argaam is down.
    """
    import requests
    import re

    global ARABIC_NAMES

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(
            "https://www.argaam.com/ar/company/companies-prices/3",
            headers=headers, timeout=15
        )
        if resp.status_code == 200:
            matches = re.findall(
                r'relf-Stocksymbol="(\d+)"[^>]*relf-companyName="([^"]+)"',
                resp.text
            )
            if matches:
                new_names = {}
                for symbol, name in matches:
                    if symbol not in new_names:
                        new_names[symbol] = name

                # Update the global dict (add new, update existing)
                ARABIC_NAMES.update(new_names)
                logging.getLogger(__name__).info(
                    f"Refreshed Arabic names from Argaam: {len(new_names)} companies"
                )
                return True
    except Exception as e:
        logging.getLogger(__name__).warning(f"Could not refresh Arabic names: {e}")

    return False


import logging


def get_yf_ticker(ticker: str) -> str:
    """Convert Tadawul ticker to yfinance format."""
    return f"{ticker}.SR"


def get_all_yf_tickers() -> list[str]:
    """Get all tickers in yfinance format."""
    return [get_yf_ticker(t) for t in TADAWUL_STOCKS]


def get_naqi_tickers() -> list[str]:
    """Get only pure (naqi) stock tickers per Al-Osaimi list."""
    return [t for t in TADAWUL_STOCKS if t in NAQI_TICKERS]


def is_naqi(ticker: str) -> bool:
    """Check if a stock is naqi (pure/halal) per Al-Osaimi."""
    return ticker in NAQI_TICKERS


def check_naqi_update_needed() -> str | None:
    """Check if naqi list needs updating. Returns Arabic reminder message or None."""
    from datetime import date, datetime
    last_updated = datetime.strptime(NAQI_LAST_UPDATED, "%Y-%m-%d").date()
    days_since = (date.today() - last_updated).days
    if days_since >= NAQI_UPDATE_DAYS:
        return (
            f"\u26a0\ufe0f <b>تنبيه: تحديث قائمة الأسهم النقية</b>\n"
            f"مضى {days_since} يوماً على آخر تحديث لقائمة العصيمي.\n"
            f"يرجى مراجعة القائمة المحدثة على Argaam.com\n"
            f"آخر تحديث: {NAQI_LAST_UPDATED}"
        )
    return None


def get_tickers_by_sector(sector: str) -> dict:
    """Get all tickers for a given sector."""
    return {k: v for k, v in TADAWUL_STOCKS.items() if v["sector"] == sector}


def get_all_sectors() -> list[str]:
    """Get list of all unique sectors."""
    return sorted(set(v["sector"] for v in TADAWUL_STOCKS.values()))


def get_stock_info(ticker: str) -> dict | None:
    """Get stock info by ticker number, including Arabic name."""
    info = TADAWUL_STOCKS.get(ticker)
    if info:
        info = dict(info)
        info["name_ar"] = ARABIC_NAMES.get(ticker, info["name"])
    return info


def get_display_name(ticker: str) -> str:
    """Get Arabic display name for a stock."""
    return ARABIC_NAMES.get(ticker, TADAWUL_STOCKS.get(ticker, {}).get("name", ticker))
