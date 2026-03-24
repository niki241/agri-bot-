"""
Seed the database with initial crop advisory data.
Run: python seed_data.py
"""
import asyncio
from app.database import engine, async_session, Base
from app.models.crop_advisory import CropAdvisory
from app.models.crop_calendar import CropCalendar


ADVISORIES = [
    # --- Rice (వరి / धान) ---
    {
        "crop": "Rice",
        "pest_disease": "Brown Plant Hopper (BPH)",
        "symptoms_te": "మొక్కలు పసుపు రంగుకు మారి ఎండిపోతాయి. 'హాపర్ బర్న్' లక్షణాలు. పొలంలో వృత్తాకార మచ్చలు.",
        "symptoms_hi": "पौधे पीले होकर सूख जाते हैं। 'हॉपर बर्न' के लक्षण। खेत में गोलाकार धब्बे।",
        "symptoms_en": "Plants turn yellow and dry up showing 'hopper burn' symptoms. Circular patches in the field.",
        "treatment": "Spray Imidacloprid 17.8% SL @ 0.5ml/litre or Thiamethoxam 25% WG @ 0.5g/litre. Drain water from field.",
        "treatment_te": "ఇమిడాక్లోప్రిడ్ 17.8% SL @ 0.5ml/లీటరు లేదా థయామిథాక్సమ్ 25% WG @ 0.5g/లీటరు స్ప్రే చేయండి. పొలం నుండి నీటిని తీసేయండి.",
        "treatment_hi": "इमिडाक्लोप्रिड 17.8% SL @ 0.5ml/लीटर या थायमिथोक्सम 25% WG @ 0.5g/लीटर का छिड़काव करें। खेत से पानी निकालें।",
        "dosage": "0.5ml/litre water; 500 litres spray solution per hectare",
        "urgency": "high",
        "source": "ICAR-NRRI Crop Protection Guide",
    },
    {
        "crop": "Rice",
        "pest_disease": "Blast Disease (Pyricularia oryzae)",
        "symptoms_te": "ఆకులపై కంటి ఆకారపు మచ్చలు, మధ్యలో బూడిద రంగు, అంచులు గోధుమ రంగు. కంకి మెడ విరిగిపోతుంది.",
        "symptoms_hi": "पत्तियों पर आँख के आकार के धब्बे, बीच में भूरा, किनारे भूरे। गर्दन टूट सकती है।",
        "symptoms_en": "Eye-shaped spots on leaves with grey center and brown margins. Neck blast causes panicle breakage.",
        "treatment": "Spray Tricyclazole 75% WP @ 0.6g/litre or Isoprothiolane 40% EC @ 1.5ml/litre. Avoid excess nitrogen.",
        "treatment_te": "ట్రైసైక్లజోల్ 75% WP @ 0.6g/లీటరు లేదా ఐసోప్రోథియోలేన్ 40% EC @ 1.5ml/లీటరు స్ప్రే చేయండి. ఎక్కువ నత్రజని వాడకం తగ్గించండి.",
        "treatment_hi": "ट्राइसाइक्लाज़ोल 75% WP @ 0.6g/लीटर या आइसोप्रोथियोलेन 40% EC @ 1.5ml/लीटर का छिड़काव करें। अत्यधिक नाइट्रोजन से बचें।",
        "dosage": "0.6g/litre water; spray at first symptom appearance",
        "urgency": "high",
        "source": "ICAR-NRRI Crop Protection Guide",
    },
    {
        "crop": "Rice",
        "pest_disease": "Stem Borer (Scirpophaga incertulas)",
        "symptoms_te": "డెడ్ హార్ట్ — మధ్య ఆకు ఎండిపోతుంది. వైట్ ఇయర్ — కంకి తెల్లగా మారి గింజలు పట్టవు.",
        "symptoms_hi": "डेड हार्ट — बीच की पत्ती सूख जाती है। व्हाइट इयर — बाली सफेद होकर दाने नहीं भरते।",
        "symptoms_en": "Dead heart in vegetative stage. White ear in reproductive stage — empty panicles.",
        "treatment": "Install pheromone traps @ 5/acre. Spray Chlorantraniliprole 18.5% SC @ 0.3ml/litre or Cartap Hydrochloride 4G @ 25kg/ha in standing water.",
        "treatment_te": "ఫెరోమోన్ ట్రాప్స్ @ 5/ఎకరం ఏర్పాటు చేయండి. క్లోరాంట్రానిలిప్రోల్ 18.5% SC @ 0.3ml/లీటరు స్ప్రే చేయండి.",
        "treatment_hi": "फेरोमोन ट्रैप @ 5/एकड़ लगाएं। क्लोरेंट्रानिलिप्रोल 18.5% SC @ 0.3ml/लीटर का छिड़काव करें।",
        "dosage": "0.3ml/litre; apply within 30 days of transplanting",
        "urgency": "high",
        "source": "ICAR-NRRI",
    },

    # --- Cotton (పత్తి / कपास) ---
    {
        "crop": "Cotton",
        "pest_disease": "Pink Bollworm (Pectinophora gossypiella)",
        "symptoms_te": "గులాబీ రంగు లార్వాలు కాయల లోపల ఉంటాయి. కాయల నుండి రోసెట్ పువ్వులు వస్తాయి. దూది నాణ్యత తగ్గుతుంది.",
        "symptoms_hi": "गुलाबी रंग के लार्वा गूलरों के अंदर होते हैं। रोसेट फूल बनते हैं। रूई की गुणवत्ता गिरती है।",
        "symptoms_en": "Pink larvae inside bolls. Rosette flowers appear. Lint quality deteriorates.",
        "treatment": "Release Trichogramma wasps @ 1.5 lakh/ha. Spray Profenophos 50% EC @ 2ml/litre. Destroy crop residues after harvest.",
        "treatment_te": "ట్రైకోగ్రామా @ 1.5 లక్షలు/హెక్టారు విడుదల చేయండి. ప్రొఫెనోఫాస్ 50% EC @ 2ml/లీటరు స్ప్రే చేయండి.",
        "treatment_hi": "ट्राइकोग्रामा @ 1.5 लाख/हेक्टेयर छोड़ें। प्रोफेनोफॉस 50% EC @ 2ml/लीटर का छिड़काव करें।",
        "dosage": "2ml/litre; 2-3 sprays at 15-day intervals during boll formation",
        "urgency": "critical",
        "source": "CICR Nagpur Advisory",
    },
    {
        "crop": "Cotton",
        "pest_disease": "Whitefly (Bemisia tabaci)",
        "symptoms_te": "ఆకుల కింద తెల్ల పురుగులు. ఆకులపై జిగురు (హనీడ్యూ). నల్ల బూజు పెరుగుతుంది.",
        "symptoms_hi": "पत्तियों के नीचे सफेद मक्खियाँ। पत्तियों पर चिपचिपा पदार्थ (हनीड्यू)। काली फफूंद बढ़ती है।",
        "symptoms_en": "White insects under leaves. Sticky honeydew on leaves. Sooty mould develops.",
        "treatment": "Spray Diafenthiuron 50% WP @ 1.2g/litre or Spiromesifen 22.9% SC @ 0.8ml/litre. Use yellow sticky traps.",
        "treatment_te": "డయాఫెంథియూరాన్ 50% WP @ 1.2g/లీటరు లేదా స్పైరోమెసిఫెన్ 22.9% SC @ 0.8ml/లీటరు స్ప్రే చేయండి. పసుపు జిగురు ట్రాప్స్ వాడండి.",
        "treatment_hi": "डायफेंथ्यूरॉन 50% WP @ 1.2g/लीटर या स्पाइरोमेसिफेन 22.9% SC @ 0.8ml/लीटर का छिड़काव करें। पीले चिपचिपे ट्रैप लगाएं।",
        "dosage": "1.2g/litre; rotate chemicals to avoid resistance",
        "urgency": "high",
        "source": "CICR Nagpur",
    },

    # --- Chilli (మిర్చి / मिर्च) ---
    {
        "crop": "Chilli",
        "pest_disease": "Thrips (Scirtothrips dorsalis)",
        "symptoms_te": "ఆకులు పైకి ముడుచుకుపోతాయి. ఆకుల కింద వెండి రంగు మచ్చలు. మొక్కలు గిడసబారతాయి.",
        "symptoms_hi": "पत्तियाँ ऊपर की ओर मुड़ जाती हैं। पत्तियों के नीचे चांदी जैसे धब्बे। पौधे बौने हो जाते हैं।",
        "symptoms_en": "Leaves curl upwards. Silver patches under leaves. Plants become stunted.",
        "treatment": "Spray Fipronil 5% SC @ 1.5ml/litre or Spinetoram 11.7% SC @ 0.5ml/litre. Apply neem oil 2% as preventive.",
        "treatment_te": "ఫిప్రోనిల్ 5% SC @ 1.5ml/లీటరు లేదా స్పినెటోరామ్ 11.7% SC @ 0.5ml/లీటరు స్ప్రే చేయండి. నివారణకు వేప నూనె 2% వాడండి.",
        "treatment_hi": "फिप्रोनिल 5% SC @ 1.5ml/लीटर या स्पाइनेटोरम 11.7% SC @ 0.5ml/लीटर का छिड़काव करें। रोकथाम के लिए नीम तेल 2% लगाएं।",
        "dosage": "1.5ml/litre; spray early morning or late evening",
        "urgency": "high",
        "source": "ICAR-IIHR",
    },
    {
        "crop": "Chilli",
        "pest_disease": "Leaf Curl Virus (Murda Complex)",
        "symptoms_te": "ఆకులు చిన్నగా, ముడుచుకుపోయి, మందంగా మారతాయి. మొక్కల పెరుగుదల ఆగిపోతుంది. కాయలు తగ్గిపోతాయి.",
        "symptoms_hi": "पत्तियाँ छोटी, मुड़ी हुई, मोटी हो जाती हैं। पौधों की बढ़वार रुक जाती है। फल कम लगते हैं।",
        "symptoms_en": "Leaves become small, curled, thick. Plant growth stops. Fruit setting reduces drastically.",
        "treatment": "Control whitefly vector: spray Diafenthiuron 50% WP @ 1.2g/litre. Uproot and destroy infected plants. Use virus-resistant varieties.",
        "treatment_te": "తెల్ల దోమను నియంత్రించండి: డయాఫెంథియూరాన్ 50% WP @ 1.2g/లీటరు. సోకిన మొక్కలను పీకి నాశనం చేయండి.",
        "treatment_hi": "सफेद मक्खी नियंत्रित करें: डायफेंथ्यूरॉन 50% WP @ 1.2g/लीटर। संक्रमित पौधे उखाड़कर नष्ट करें।",
        "dosage": "1.2g/litre; spray every 10 days if whitefly seen",
        "urgency": "critical",
        "source": "ICAR-IIHR",
    },

    # --- Wheat (గోధుమ / गेहूं) ---
    {
        "crop": "Wheat",
        "pest_disease": "Yellow Rust (Puccinia striiformis)",
        "symptoms_te": "ఆకులపై పసుపు రంగు చారలు ఆకు ఈనెలకు సమాంతరంగా ఏర్పడతాయి.",
        "symptoms_hi": "पत्तियों पर पीली धारियाँ पत्ती की नसों के समानांतर बनती हैं।",
        "symptoms_en": "Yellow stripes parallel to leaf veins on upper surface. Pustules release yellow spores.",
        "treatment": "Spray Propiconazole 25% EC @ 1ml/litre or Tebuconazole 25.9% EC @ 1ml/litre at first appearance.",
        "treatment_te": "ప్రొపికొనజోల్ 25% EC @ 1ml/లీటరు లేదా టెబుకొనజోల్ 25.9% EC @ 1ml/లీటరు మొదటి లక్షణాలు కనిపించినప్పుడు స్ప్రే చేయండి.",
        "treatment_hi": "प्रोपिकोनाज़ोल 25% EC @ 1ml/लीटर या टेबुकोनाज़ोल 25.9% EC @ 1ml/लीटर पहले लक्षण दिखते ही छिड़काव करें।",
        "dosage": "1ml/litre; repeat after 15 days if needed",
        "urgency": "high",
        "source": "ICAR-IIWBR Karnal",
    },
    {
        "crop": "Wheat",
        "pest_disease": "Aphid (Sitobion avenae)",
        "symptoms_te": "ఆకులపై మరియు కంకులపై ఆకుపచ్చ/నల్ల పురుగులు. హనీడ్యూ మరియు నల్ల బూజు.",
        "symptoms_hi": "पत्तियों और बालियों पर हरे/काले कीड़े। हनीड्यू और काली फफूंद।",
        "symptoms_en": "Green/black insects on leaves and ears. Honeydew secretion leads to sooty mould.",
        "treatment": "Spray Dimethoate 30% EC @ 1.5ml/litre or Thiamethoxam 25% WG @ 0.3g/litre if ETL exceeds 10-15 aphids/ear.",
        "treatment_te": "డైమిథోయేట్ 30% EC @ 1.5ml/లీటరు లేదా థయామిథాక్సమ్ 25% WG @ 0.3g/లీటరు కంకికి 10-15 కంటే ఎక్కువ పేనులు ఉంటే స్ప్రే చేయండి.",
        "treatment_hi": "डाइमेथोएट 30% EC @ 1.5ml/लीटर या थायमिथोक्सम 25% WG @ 0.3g/लीटर बाली पर 10-15 से अधिक माहू होने पर छिड़काव करें।",
        "dosage": "1.5ml/litre; spray when ETL is crossed",
        "urgency": "medium",
        "source": "ICAR-IIWBR Karnal",
    },

    # --- Soybean (సోయాబీన్ / सोयाबीन) ---
    {
        "crop": "Soybean",
        "pest_disease": "Girdle Beetle (Obereopsis brevis)",
        "symptoms_te": "కాండంపై రెండు వలయాకార గాట్లు. పై భాగం వాడి ఎండిపోతుంది.",
        "symptoms_hi": "तने पर दो गोलाकार खरोंचें। ऊपरी भाग मुरझाकर सूख जाता है।",
        "symptoms_en": "Two girdle marks on stem. Upper portion wilts and dries. Larvae bore inside stem.",
        "treatment": "Spray Triazophos 40% EC @ 1.5ml/litre or Profenophos 50% EC @ 2ml/litre. Destroy affected plant parts.",
        "treatment_te": "ట్రయాజోఫాస్ 40% EC @ 1.5ml/లీటరు లేదా ప్రొఫెనోఫాస్ 50% EC @ 2ml/లీటరు స్ప్రే చేయండి.",
        "treatment_hi": "ट्रायज़ोफॉस 40% EC @ 1.5ml/लीटर या प्रोफेनोफॉस 50% EC @ 2ml/लीटर का छिड़काव करें।",
        "dosage": "1.5ml/litre; spray at 30-35 days after sowing",
        "urgency": "medium",
        "source": "ICAR-IISR Indore",
    },
    {
        "crop": "Soybean",
        "pest_disease": "Yellow Mosaic Virus (YMV)",
        "symptoms_te": "ఆకులపై పసుపు మచ్చలు. తీవ్రంగా ఉంటే మొత్తం ఆకు పసుపు. కాయలు తక్కువగా ఏర్పడతాయి.",
        "symptoms_hi": "पत्तियों पर पीले धब्बे। गंभीर होने पर पूरी पत्ती पीली। फलियाँ कम बनती हैं।",
        "symptoms_en": "Yellow patches on leaves. Severe infection turns whole leaf yellow. Pod formation reduces.",
        "treatment": "Control whitefly vector: spray Thiamethoxam 25% WG @ 0.3g/litre. Grow resistant varieties (JS 335, JS 93-05). Remove infected plants early.",
        "treatment_te": "తెల్ల దోమ నియంత్రణ: థయామిథాక్సమ్ 25% WG @ 0.3g/లీటరు. నిరోధక రకాలు వాడండి.",
        "treatment_hi": "सफेद मक्खी नियंत्रण: थायमिथोक्सम 25% WG @ 0.3g/लीटर। प्रतिरोधी किस्में उगाएं।",
        "dosage": "0.3g/litre; spray at first whitefly appearance",
        "urgency": "high",
        "source": "ICAR-IISR Indore",
    },

    # --- Tomato (టమాట / टमाटर) ---
    {
        "crop": "Tomato",
        "pest_disease": "Tomato Leaf Curl Virus",
        "symptoms_te": "ఆకులు పైకి ముడుచుకుపోతాయి, మందంగా మారతాయి. మొక్కలు గిడసబారతాయి. కాయల దిగుబడి తీవ్రంగా తగ్గుతుంది.",
        "symptoms_hi": "पत्तियाँ ऊपर मुड़ जाती हैं, मोटी हो जाती हैं। पौधे बौने हो जाते हैं। फलों की उपज बहुत कम हो जाती है।",
        "symptoms_en": "Leaves curl upward and become thick, leathery. Plants stunted. Drastic yield reduction.",
        "treatment": "Control whitefly: Diafenthiuron 50% WP @ 1.2g/litre. Use resistant varieties (Arka Rakshak). Silver mulch repels whitefly.",
        "treatment_te": "తెల్ల దోమ నియంత్రణ: డయాఫెంథియూరాన్ 50% WP @ 1.2g/లీటరు. నిరోధక రకాలు (అర్క రక్షక్) వాడండి. వెండి మల్చ్ తెల్ల దోమను దూరం చేస్తుంది.",
        "treatment_hi": "सफेद मक्खी नियंत्रण: डायफेंथ्यूरॉन 50% WP @ 1.2g/लीटर। प्रतिरोधी किस्में (अर्का रक्षक) उगाएं। सिल्वर मल्च सफेद मक्खी को दूर रखती है।",
        "dosage": "1.2g/litre; use mulch from transplanting",
        "urgency": "high",
        "source": "ICAR-IIHR Bengaluru",
    },
    {
        "crop": "Tomato",
        "pest_disease": "Late Blight (Phytophthora infestans)",
        "symptoms_te": "ఆకులపై నీటి మచ్చలు, తరువాత గోధుమ-నల్లగా మారతాయి. కాయలపై గోధుమ మచ్చలు. తేమ వాతావరణంలో వేగంగా వ్యాపిస్తుంది.",
        "symptoms_hi": "पत्तियों पर पानी जैसे धब्बे, फिर भूरे-काले हो जाते हैं। फलों पर भूरे धब्बे। नम मौसम में तेजी से फैलता है।",
        "symptoms_en": "Water-soaked lesions turning brown-black on leaves. Brown patches on fruits. Spreads rapidly in wet weather.",
        "treatment": "Spray Mancozeb 75% WP @ 2.5g/litre preventively. Curative: Cymoxanil 8% + Mancozeb 64% WP @ 3g/litre. Improve air circulation.",
        "treatment_te": "నివారణకు మాంకోజెబ్ 75% WP @ 2.5g/లీటరు స్ప్రే చేయండి. చికిత్సకు సైమోక్సానిల్ 8% + మాంకోజెబ్ 64% WP @ 3g/లీటరు.",
        "treatment_hi": "रोकथाम: मैनकोज़ेब 75% WP @ 2.5g/लीटर छिड़काव। उपचार: साइमोक्सानिल 8% + मैनकोज़ेब 64% WP @ 3g/लीटर।",
        "dosage": "2.5g/litre preventive; 3g/litre curative; spray every 7-10 days in wet season",
        "urgency": "critical",
        "source": "ICAR-IIHR",
    },

    # --- Groundnut (వేరుశెనగ / मूंगफली) ---
    {
        "crop": "Groundnut",
        "pest_disease": "Tikka Disease (Cercospora leaf spot)",
        "symptoms_te": "ఆకులపై గోధుమ రంగు గుండ్రని మచ్చలు. తీవ్రమైతే ఆకులు రాలిపోతాయి.",
        "symptoms_hi": "पत्तियों पर भूरे गोल धब्बे। गंभीर होने पर पत्तियाँ झड़ जाती हैं।",
        "symptoms_en": "Brown circular spots on leaves. Severe infection causes defoliation.",
        "treatment": "Spray Chlorothalonil 75% WP @ 2g/litre or Mancozeb 75% WP @ 2.5g/litre. Apply at 35, 50, and 65 days after sowing.",
        "treatment_te": "క్లోరోథలోనిల్ 75% WP @ 2g/లీటరు లేదా మాంకోజెబ్ 75% WP @ 2.5g/లీటరు. విత్తిన 35, 50, 65 రోజులకు స్ప్రే చేయండి.",
        "treatment_hi": "क्लोरोथेलोनिल 75% WP @ 2g/लीटर या मैनकोज़ेब 75% WP @ 2.5g/लीटर। बुवाई के 35, 50, 65 दिन बाद छिड़काव करें।",
        "dosage": "2g/litre; 3 sprays at 15-day intervals",
        "urgency": "medium",
        "source": "ICAR-DGR Junagadh",
    },

    # --- Turmeric (పసుపు / हल्दी) ---
    {
        "crop": "Turmeric",
        "pest_disease": "Rhizome Rot (Pythium aphanidermatum)",
        "symptoms_te": "మొక్క కింది నుండి ఆకులు పసుపు మారి వాడిపోతాయి. దుంపలు మెత్తగా కుళ్ళిపోతాయి. దుర్వాసన వస్తుంది.",
        "symptoms_hi": "नीचे से पत्तियाँ पीली होकर मुरझाती हैं। कंद मुलायम होकर सड़ जाते हैं। बदबू आती है।",
        "symptoms_en": "Lower leaves yellow and wilt. Rhizomes become soft and rotten with foul smell.",
        "treatment": "Drench soil with Metalaxyl 35% WS @ 2.5g/litre. Remove and destroy infected plants. Improve drainage. Treat seed rhizomes before planting.",
        "treatment_te": "మెటాలాక్సిల్ 35% WS @ 2.5g/లీటరు మట్టిలో పోయండి. సోకిన మొక్కలను తీసి నాశనం చేయండి. నీటి పారుదల మెరుగుపరచండి.",
        "treatment_hi": "मेटालैक्सिल 35% WS @ 2.5g/लीटर मिट्टी में डालें। संक्रमित पौधे निकालकर नष्ट करें। जल निकासी सुधारें।",
        "dosage": "2.5g/litre soil drench; repeat after 15 days",
        "urgency": "critical",
        "source": "ICAR-IISR Calicut",
    },

    # --- General nutrient deficiency ---
    {
        "crop": "General",
        "pest_disease": "Nitrogen Deficiency",
        "symptoms_te": "కింది ఆకులు పసుపు మారతాయి. మొక్కలు లేత ఆకుపచ్చగా, గిడసబారతాయి. పెరుగుదల తగ్గుతుంది.",
        "symptoms_hi": "निचली पत्तियाँ पीली होती हैं। पौधे हल्के हरे, बौने होते हैं। बढ़वार कम होती है।",
        "symptoms_en": "Lower leaves turn yellow first. Plants are pale green and stunted. Growth is reduced.",
        "treatment": "Apply Urea @ 25-50 kg/acre depending on crop. Foliar spray: Urea 2% (20g/litre). Consider split application for better uptake.",
        "treatment_te": "యూరియా @ 25-50 కిలో/ఎకరం వేయండి. ఫోలియర్ స్ప్రే: యూరియా 2% (20g/లీటరు).",
        "treatment_hi": "यूरिया @ 25-50 किलो/एकड़ डालें। पर्णीय छिड़काव: यूरिया 2% (20g/लीटर)।",
        "dosage": "25-50 kg/acre soil; 20g/litre foliar",
        "urgency": "medium",
        "source": "ICAR Soil Health Guide",
    },
    {
        "crop": "General",
        "pest_disease": "Iron Deficiency (Chlorosis)",
        "symptoms_te": "కొత్త ఆకులు పసుపు, ఈనెలు ఆకుపచ్చగా ఉంటాయి (ఇంటర్‌వీనల్ క్లోరోసిస్). తీవ్రమైతే ఆకులు తెల్లగా మారతాయి.",
        "symptoms_hi": "नई पत्तियाँ पीली, नसें हरी रहती हैं (इंटरवीनल क्लोरोसिस)। गंभीर होने पर पत्तियाँ सफेद हो जाती हैं।",
        "symptoms_en": "New leaves yellow with green veins (interveinal chlorosis). Severe cases show white leaves.",
        "treatment": "Foliar spray Ferrous Sulphate 0.5% (5g/litre) + Citric Acid 0.1%. Soil application: FeSO4 @ 25kg/ha with FYM.",
        "treatment_te": "ఫెర్రస్ సల్ఫేట్ 0.5% (5g/లీటరు) + సిట్రిక్ ఆసిడ్ 0.1% ఫోలియర్ స్ప్రే. మట్టిలో: FeSO4 @ 25kg/హెక్టారు పశువుల ఎరువుతో.",
        "treatment_hi": "फेरस सल्फेट 0.5% (5g/लीटर) + सिट्रिक एसिड 0.1% पर्णीय छिड़काव। मिट्टी में: FeSO4 @ 25kg/हेक्टेयर गोबर खाद के साथ।",
        "dosage": "5g/litre foliar; 25kg/ha soil with FYM",
        "urgency": "low",
        "source": "ICAR Soil Health Guide",
    },
]


CALENDAR_ENTRIES = [
    # Rice - Telangana
    {"crop": "Rice", "region": "Telangana", "activity": "Land preparation & nursery sowing", "month_start": 6, "month_end": 6,
     "description_te": "నేల తయారీ, నారుమడి వేయడం. విత్తనాలను కార్బెండజిమ్ తో శుద్ధి చేయండి.",
     "description_hi": "भूमि तैयारी, नर्सरी बुवाई। बीजों को कार्बेन्डाज़िम से उपचारित करें।"},
    {"crop": "Rice", "region": "Telangana", "activity": "Transplanting", "month_start": 7, "month_end": 7,
     "description_te": "25-30 రోజుల నారును నాటండి. వరుసల మధ్య 20x15 సెం.మీ. దూరం.",
     "description_hi": "25-30 दिन की पौध रोपाई करें। पंक्तियों में 20x15 सेमी दूरी।"},
    {"crop": "Rice", "region": "Telangana", "activity": "Top dressing & pest watch", "month_start": 8, "month_end": 8,
     "description_te": "యూరియా టాప్ డ్రెస్సింగ్. BPH, ఆకుముడత తనిఖీ చేయండి.",
     "description_hi": "यूरिया टॉप ड्रेसिंग। BPH, पत्ता लपेट कीट की जांच करें।"},
    {"crop": "Rice", "region": "Telangana", "activity": "Harvest", "month_start": 10, "month_end": 11,
     "description_te": "80% గింజలు పక్వం అయ్యాక కోయండి. తేమ 20% లోపు ఉండాలి.",
     "description_hi": "80% दाने पकने पर कटाई करें। नमी 20% से कम होनी चाहिए।"},

    # Cotton - Telangana
    {"crop": "Cotton", "region": "Telangana", "activity": "Sowing", "month_start": 6, "month_end": 7,
     "description_te": "జూన్-జూలై లో విత్తడం. వరుసల మధ్య 90x60 సెం.మీ. దూరం. విత్తన శుద్ధి చేయండి.",
     "description_hi": "जून-जुलाई में बुवाई। पंक्तियों में 90x60 सेमी दूरी। बीज उपचार करें।"},
    {"crop": "Cotton", "region": "Telangana", "activity": "Vegetative growth & pest management", "month_start": 8, "month_end": 9,
     "description_te": "సక్కింగ్ పెస్ట్స్ (తెల్ల దోమ, పేనులు) తనిఖీ. నీమ్ ఆయిల్ స్ప్రే.",
     "description_hi": "रस चूसक कीट (सफेद मक्खी, जूँ) जांच। नीम तेल छिड़काव।"},
    {"crop": "Cotton", "region": "Telangana", "activity": "Boll formation & picking", "month_start": 10, "month_end": 12,
     "description_te": "పింక్ బోల్‌వార్మ్ తనిఖీ. ఫెరోమోన్ ట్రాప్స్ ఏర్పాటు. కాయలు పగిలాక ఏరడం.",
     "description_hi": "गुलाबी सुंडी जांच। फेरोमोन ट्रैप लगाएं। गूलर खिलने पर चुनाई।"},

    # Chilli - Andhra Pradesh
    {"crop": "Chilli", "region": "Andhra Pradesh", "activity": "Nursery & transplanting", "month_start": 7, "month_end": 8,
     "description_te": "జూలై లో నారుమడి. 40-45 రోజుల నారును ఆగస్టులో నాటండి.",
     "description_hi": "जुलाई में नर्सरी। 40-45 दिन की पौध अगस्त में रोपाई।"},
    {"crop": "Chilli", "region": "Andhra Pradesh", "activity": "Harvest", "month_start": 12, "month_end": 3,
     "description_te": "డిసెంబర్ నుండి మార్చి వరకు కోత. ఎరుపు రంగుకు మారాక ఏరడం.",
     "description_hi": "दिसंबर से मार्च तक तुड़ाई। लाल होने पर तोड़ें।"},

    # Wheat - Hindi belt
    {"crop": "Wheat", "region": "Uttar Pradesh", "activity": "Sowing", "month_start": 11, "month_end": 12,
     "description_te": "నవంబర్-డిసెంబర్ లో విత్తడం. HD-2967, PBW-343 రకాలు.",
     "description_hi": "नवंबर-दिसंबर में बुवाई। HD-2967, PBW-343 किस्में।"},
    {"crop": "Wheat", "region": "Uttar Pradesh", "activity": "Irrigation & top dressing", "month_start": 12, "month_end": 2,
     "description_te": "క్రౌన్ రూట్ స్టేజ్ (21 రోజులు), బూటింగ్, ఫ్లవరింగ్ దశల్లో నీరు పెట్టండి.",
     "description_hi": "क्राउन रूट (21 दिन), बूटिंग, फूल आने पर सिंचाई करें।"},
    {"crop": "Wheat", "region": "Uttar Pradesh", "activity": "Harvest", "month_start": 3, "month_end": 4,
     "description_te": "మార్చి-ఏప్రిల్ లో కోత. గింజల్లో తేమ 12-14% ఉన్నప్పుడు.",
     "description_hi": "मार्च-अप्रैल में कटाई। दानों में नमी 12-14% होने पर।"},
]


async def seed_database():
    """Seed the database with initial data."""
    from sqlalchemy import select

    async with async_session() as db:
        # Check if data already exists
        result = await db.execute(select(CropAdvisory).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        # Seed advisories
        for adv_data in ADVISORIES:
            advisory = CropAdvisory(**adv_data)
            db.add(advisory)

        # Seed calendar
        for cal_data in CALENDAR_ENTRIES:
            cal = CropCalendar(**cal_data)
            db.add(cal)

        await db.commit()
        print(f"✅ Seeded {len(ADVISORIES)} crop advisories and {len(CALENDAR_ENTRIES)} calendar entries.")


if __name__ == "__main__":
    asyncio.run(seed_database())
