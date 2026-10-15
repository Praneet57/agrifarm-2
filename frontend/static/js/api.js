const API_BASE="/api/v1";
const LANGUAGES={
  en:{},
  ta:{
    "AgriMarket":"அக்ரி மார்க்கெட்","Create Account":"கணக்கை உருவாக்கு","Join AgriMarket for free":"இலவசமாக அக்ரி மார்க்கெட்டில் இணையுங்கள்","Name *":"பெயர் *","Phone Number *":"தொலைபேசி எண் *","Email":"மின்னஞ்சல்","Optional":"விருப்பத்தேர்வு","Address":"முகவரி","State *":"மாநிலம் *","Select state":"மாநிலத்தைத் தேர்ந்தெடுக்கவும்","District *":"மாவட்டம் *","Taluk":"தாலுகா","Area":"பகுதி","Door No. / Farm":"கதவு எண் / பண்ணை","Password *":"கடவுச்சொல் *","Confirm Password *":"கடவுச்சொல்லை உறுதிப்படுத்தவும் *","What do you want to do? *":"நீங்கள் என்ன செய்ய விரும்புகிறீர்கள்? *","Choose an option":"ஒரு விருப்பத்தைத் தேர்ந்தெடுக்கவும்","Want to Sell":"விற்க விரும்புகிறேன்","Want to Buy":"வாங்க விரும்புகிறேன்","What do you want to sell? *":"நீங்கள் எதை விற்க விரும்புகிறீர்கள்? *","What do you want to buy? *":"நீங்கள் எதை வாங்க விரும்புகிறீர்கள்? *","Farm and agriculture details *":"பண்ணை மற்றும் விவசாய விவரங்கள் *","Enter the products you want to sell":"நீங்கள் விற்க விரும்பும் பொருட்களை உள்ளிடவும்","Enter the products you want to buy":"நீங்கள் வாங்க விரும்பும் பொருட்களை உள்ளிடவும்","Create Account":"கணக்கை உருவாக்கு","Already have an account?":"ஏற்கனவே கணக்கு உள்ளதா?","Sign In":"உள்நுழைய","Language":"மொழி","Choose your language":"உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்","English":"ஆங்கிலம்","Tamil":"தமிழ்","Telugu":"தெலுங்கு","Your full name":"உங்கள் முழுப் பெயர்","10-digit mobile":"10 இலக்க கைபேசி எண்","Select language":"மொழியைத் தேர்ந்தெடுக்கவும்","Registration language":"பதிவு மொழி",
    "Sign in to your account":"உங்கள் கணக்கில் உள்நுழையவும்","Phone Number":"தொலைபேசி எண்","Password":"கடவுச்சொல்","Enter your phone number":"உங்கள் தொலைபேசி எண்ணை உள்ளிடவும்","Enter your password":"உங்கள் கடவுச்சொல்லை உள்ளிடவும்","Forgot password?":"கடவுச்சொல்லை மறந்துவிட்டீர்களா?","Don't have an account?":"கணக்கு இல்லையா?","Register Free":"இலவசமாகப் பதிவு செய்யுங்கள்",
    "Marketplace":"சந்தை","My Listings":"எனது பட்டியல்கள்","Add Product":"பொருளைச் சேர்க்கவும்","Orders":"ஆர்டர்கள்","Messages":"செய்திகள்","Profile":"சுயவிவரம்","Settings":"அமைப்புகள்","Save Changes":"மாற்றங்களைச் சேமிக்கவும்","My Profile":"எனது சுயவிவரம்","Edit Profile":"சுயவிவரத்தைத் திருத்தவும்","Full Name":"முழுப் பெயர்","Bio":"சுயவிவரக் குறிப்பு","District":"மாவட்டம்","Overview":"கண்ணோட்டம்","My Demands":"எனது தேவைகள்","Post Demand":"தேவையைப் பதிவிடவும்","My Orders":"எனது ஆர்டர்கள்","Buyer Overview":"வாங்குபவர் கண்ணோட்டம்","Farmer Profile":"விவசாயி சுயவிவரம்","Select your preferred language":"உங்களுக்கு விருப்பமான மொழியைத் தேர்ந்தெடுக்கவும்","Your language preference is saved to your account.":"உங்கள் மொழி விருப்பம் கணக்கில் சேமிக்கப்படும்.","Save Language":"மொழியைச் சேமிக்கவும்","Language preference saved":"மொழி விருப்பம் சேமிக்கப்பட்டது",
    "Search":"தேடு","Clear":"அழி","Category":"வகை","All":"அனைத்தும்","Fruits":"பழங்கள்","Vegetables":"காய்கறிகள்","Grains":"தானியங்கள்","Pulses":"பருப்பு வகைகள்","Spices":"மசாலாப் பொருட்கள்","Other":"மற்றவை","Product Name *":"பொருளின் பெயர் *","Quantity (kg) *":"அளவு (கிலோ) *","Price/kg (₹) *":"விலை/கிலோ (₹) *","Phone (read-only)":"தொலைபேசி (மாற்ற முடியாது)","Village":"கிராமம்","Current Password":"தற்போதைய கடவுச்சொல்","New Password":"புதிய கடவுச்சொல்","Confirm New Password":"புதிய கடவுச்சொல்லை உறுதிப்படுத்தவும்","Change Password":"கடவுச்சொல்லை மாற்றவும்","Logout":"வெளியேறு","Dashboard":"முகப்புப் பலகை","Search marketplace":"சந்தையில் தேடுங்கள்",
    "Fill in all required fields.":"தேவையான அனைத்து புலங்களையும் நிரப்பவும்.","Please enter your state and district.":"உங்கள் மாநிலம் மற்றும் மாவட்டத்தை உள்ளிடவும்.","Choose whether you want to sell or buy.":"நீங்கள் விற்க விரும்புகிறீர்களா அல்லது வாங்க விரும்புகிறீர்களா என்பதைத் தேர்ந்தெடுக்கவும்.","Enter what you want to sell.":"நீங்கள் விற்க விரும்புவதை உள்ளிடவும்.","Enter what you want to buy.":"நீங்கள் வாங்க விரும்புவதை உள்ளிடவும்.","Enter your farm and agriculture details.":"உங்கள் பண்ணை மற்றும் விவசாய விவரங்களை உள்ளிடவும்.","Passwords do not match.":"கடவுச்சொற்கள் பொருந்தவில்லை.","Welcome to AgriMarket! 🎉":"அக்ரி மார்க்கெட்டிற்கு வரவேற்கிறோம்! 🎉","Please fill in all fields.":"அனைத்து புலங்களையும் நிரப்பவும்.",
    "Marketplace Listings":"சந்தை பட்டியல்கள்","Have produce to sell?":"விளைபொருட்களை விற்க விரும்புகிறீர்களா?","Add your harvest to the marketplace and reach local buyers.":"உங்கள் அறுவடையை சந்தையில் சேர்த்து உள்ளூர் வாங்குபவர்களைச் சென்றடையுங்கள்.","Browse produce":"விளைபொருட்களைப் பார்க்கவும்","List produce":"விளைபொருட்களைப் பட்டியலிடவும்","Good food starts with good soil.":"நல்ல உணவு நல்ல மண்ணில் தொடங்குகிறது.","Put your harvest on the marketplace.":"உங்கள் அறுவடையை சந்தையில் பட்டியலிடுங்கள்.","Shop what is growing nearby.":"அருகில் விளைவதை வாங்குங்கள்.","Grow together, one harvest at a time.":"ஒவ்வொரு அறுவடையிலும் ஒன்றாக வளர்வோம்.","Search produce, category, or district":"விளைபொருள், வகை அல்லது மாவட்டத்தைத் தேடுங்கள்","My Listings":"எனது பட்டியல்கள்","Add Product":"பொருளைச் சேர்க்கவும்","Post a Demand":"தேவையைப் பதிவிடவும்","Active Demands":"செயலில் உள்ள தேவைகள்","Recent Orders":"சமீபத்திய ஆர்டர்கள்","Fresh Products":"புதிய விளைபொருட்கள்","All marketplace listings":"சந்தையின் அனைத்து பட்டியல்களும்","Nearby + all areas":"அருகிலுள்ளவை மற்றும் அனைத்து பகுதிகளும்","Fresh picks near you":"உங்களுக்கு அருகிலுள்ள புதிய விளைபொருட்கள்","Best match":"சிறந்த பொருத்தம்","Product Name *":"பொருளின் பெயர் *","Category *":"வகை *","Select":"தேர்ந்தெடுக்கவும்","Description":"விளக்கம்","Price per kg":"கிலோவிற்கான விலை","Quantity":"அளவு","Organic only":"இயற்கை முறையில் விளைவித்தவை மட்டும்","Max ₹/kg":"அதிகபட்சம் ₹/கிலோ","Search marketplace":"சந்தையில் தேடுங்கள்","No listings found":"பட்டியல்கள் எதுவும் இல்லை","Your rating":"உங்கள் மதிப்பீடு","Your reviews":"உங்கள் மதிப்புரைகள்","Email":"மின்னஞ்சல்","Village":"கிராமம்","Your language preference is saved to your account.":"உங்கள் மொழி விருப்பம் கணக்கில் சேமிக்கப்படும்."
  },
  te:{
    "AgriMarket":"అగ్రి మార్కెట్","Create Account":"ఖాతాను సృష్టించండి","Join AgriMarket for free":"అగ్రి మార్కెట్‌లో ఉచితంగా చేరండి","Name *":"పేరు *","Phone Number *":"ఫోన్ నంబర్ *","Email":"ఇమెయిల్","Optional":"ఐచ్ఛికం","Address":"చిరునామా","State *":"రాష్ట్రం *","Select state":"రాష్ట్రాన్ని ఎంచుకోండి","District *":"జిల్లా *","Taluk":"తాలూకా","Area":"ప్రాంతం","Door No. / Farm":"ఇంటి నంబర్ / పొలం","Password *":"పాస్‌వర్డ్ *","Confirm Password *":"పాస్‌వర్డ్‌ను నిర్ధారించండి *","What do you want to do? *":"మీరు ఏమి చేయాలనుకుంటున్నారు? *","Choose an option":"ఒక ఎంపికను ఎంచుకోండి","Want to Sell":"అమ్మాలనుకుంటున్నాను","Want to Buy":"కొనాలనుకుంటున్నాను","What do you want to sell? *":"మీరు ఏమి అమ్మాలనుకుంటున్నారు? *","What do you want to buy? *":"మీరు ఏమి కొనాలనుకుంటున్నారు? *","Farm and agriculture details *":"పొలం మరియు వ్యవసాయ వివరాలు *","Enter the products you want to sell":"మీరు అమ్మాలనుకునే ఉత్పత్తులను నమోదు చేయండి","Enter the products you want to buy":"మీరు కొనాలనుకునే ఉత్పత్తులను నమోదు చేయండి","Already have an account?":"ఇప్పటికే ఖాతా ఉందా?","Sign In":"సైన్ ఇన్","Language":"భాష","Choose your language":"మీ భాషను ఎంచుకోండి","English":"ఆంగ్లం","Tamil":"తమిళం","Telugu":"తెలుగు","Your full name":"మీ పూర్తి పేరు","10-digit mobile":"10 అంకెల మొబైల్ నంబర్","Select language":"భాషను ఎంచుకోండి","Registration language":"నమోదు భాష",
    "Sign in to your account":"మీ ఖాతాలోకి సైన్ ఇన్ చేయండి","Phone Number":"ఫోన్ నంబర్","Password":"పాస్‌వర్డ్","Enter your phone number":"మీ ఫోన్ నంబర్‌ను నమోదు చేయండి","Enter your password":"మీ పాస్‌వర్డ్‌ను నమోదు చేయండి","Forgot password?":"పాస్‌వర్డ్ మర్చిపోయారా?","Don't have an account?":"ఖాతా లేదా?","Register Free":"ఉచితంగా నమోదు చేసుకోండి",
    "Marketplace":"మార్కెట్‌ప్లేస్","My Listings":"నా జాబితాలు","Add Product":"ఉత్పత్తిని జోడించండి","Orders":"ఆర్డర్లు","Messages":"సందేశాలు","Profile":"ప్రొఫైల్","Settings":"సెట్టింగ్‌లు","Save Changes":"మార్పులను సేవ్ చేయండి","My Profile":"నా ప్రొఫైల్","Edit Profile":"ప్రొఫైల్‌ను సవరించండి","Full Name":"పూర్తి పేరు","Bio":"పరిచయం","District":"జిల్లా","Overview":"అవలోకనం","My Demands":"నా అభ్యర్థనలు","Post Demand":"అభ్యర్థనను పోస్ట్ చేయండి","My Orders":"నా ఆర్డర్లు","Buyer Overview":"కొనుగోలుదారు అవలోకనం","Farmer Profile":"రైతు ప్రొఫైల్","Select your preferred language":"మీకు నచ్చిన భాషను ఎంచుకోండి","Your language preference is saved to your account.":"మీ భాష ప్రాధాన్యత మీ ఖాతాలో సేవ్ అవుతుంది.","Save Language":"భాషను సేవ్ చేయండి","Language preference saved":"భాష ప్రాధాన్యత సేవ్ చేయబడింది",
    "Search":"వెతకండి","Clear":"తొలగించండి","Category":"వర్గం","All":"అన్నీ","Fruits":"పండ్లు","Vegetables":"కూరగాయలు","Grains":"ధాన్యాలు","Pulses":"పప్పులు","Spices":"మసాలా దినుసులు","Other":"ఇతర","Product Name *":"ఉత్పత్తి పేరు *","Quantity (kg) *":"పరిమాణం (కిలోలు) *","Price/kg (₹) *":"ధర/కిలో (₹) *","Phone (read-only)":"ఫోన్ (చదవడానికి మాత్రమే)","Village":"గ్రామం","Current Password":"ప్రస్తుత పాస్‌వర్డ్","New Password":"కొత్త పాస్‌వర్డ్","Confirm New Password":"కొత్త పాస్‌వర్డ్‌ను నిర్ధారించండి","Change Password":"పాస్‌వర్డ్ మార్చండి","Logout":"లాగ్ అవుట్","Dashboard":"డాష్‌బోర్డ్",
    "Fill in all required fields.":"అవసరమైన అన్ని వివరాలను పూరించండి.","Please enter your state and district.":"మీ రాష్ట్రం మరియు జిల్లాను నమోదు చేయండి.","Choose whether you want to sell or buy.":"మీరు అమ్మాలనుకుంటున్నారా లేదా కొనాలనుకుంటున్నారా ఎంచుకోండి.","Enter what you want to sell.":"మీరు అమ్మాలనుకునే వివరాలను నమోదు చేయండి.","Enter what you want to buy.":"మీరు కొనాలనుకునే వివరాలను నమోదు చేయండి.","Enter your farm and agriculture details.":"మీ పొలం మరియు వ్యవసాయ వివరాలను నమోదు చేయండి.","Passwords do not match.":"పాస్‌వర్డ్‌లు సరిపోలడం లేదు.","Welcome to AgriMarket! 🎉":"అగ్రి మార్కెట్‌కు స్వాగతం! 🎉","Please fill in all fields.":"అన్ని వివరాలను పూరించండి.",
    "Marketplace Listings":"మార్కెట్‌ప్లేస్ జాబితాలు","Have produce to sell?":"అమ్మడానికి పంట ఉందా?","Add your harvest to the marketplace and reach local buyers.":"మీ పంటను మార్కెట్‌ప్లేస్‌లో జోడించి స్థానిక కొనుగోలుదారులను చేరుకోండి.","Browse produce":"ఉత్పత్తులను చూడండి","List produce":"ఉత్పత్తులను జాబితా చేయండి","Good food starts with good soil.":"మంచి ఆహారం మంచి నేలతో ప్రారంభమవుతుంది.","Put your harvest on the marketplace.":"మీ పంటను మార్కెట్‌ప్లేస్‌లో జాబితా చేయండి.","Shop what is growing nearby.":"దగ్గరలో పండిన వాటిని కొనండి.","Grow together, one harvest at a time.":"ప్రతి పంటతో కలిసి ఎదుగుదాం.","Search produce, category, or district":"ఉత్పత్తి, వర్గం లేదా జిల్లా కోసం వెతకండి","My Listings":"నా జాబితాలు","Add Product":"ఉత్పత్తిని జోడించండి","Post a Demand":"అభ్యర్థనను పోస్ట్ చేయండి","Active Demands":"క్రియాశీల అభ్యర్థనలు","Recent Orders":"ఇటీవలి ఆర్డర్లు","Fresh Products":"తాజా ఉత్పత్తులు","All marketplace listings":"మార్కెట్‌ప్లేస్‌లోని అన్ని జాబితాలు","Nearby + all areas":"సమీపంలోని మరియు అన్ని ప్రాంతాలు","Fresh picks near you":"మీకు సమీపంలోని తాజా ఉత్పత్తులు","Best match":"ఉత్తమ సరిపోలిక","Product Name *":"ఉత్పత్తి పేరు *","Category *":"వర్గం *","Select":"ఎంచుకోండి","Description":"వివరణ","Price per kg":"కిలో ధర","Quantity":"పరిమాణం","Organic only":"సేంద్రీయ ఉత్పత్తులు మాత్రమే","Max ₹/kg":"గరిష్ఠం ₹/కిలో","No listings found":"జాబితాలు ఏవీ కనబడలేదు","Your rating":"మీ రేటింగ్","Your reviews":"మీ సమీక్షలు","Village":"గ్రామం","Your language preference is saved to your account.":"మీ భాష ప్రాధాన్యత మీ ఖాతాలో సేవ్ అవుతుంది."
  }
};
const translationOriginals=new WeakMap();
const translatedAttributes=new WeakMap();
function currentLanguage(){const lang=localStorage.getItem("preferred_language");return lang==="ta"||lang==="te"?lang:"en"}
function translateText(value,language=currentLanguage()){
  const source=value.trim();
  for(const code of ["ta","te"]){
    const match=Object.entries(LANGUAGES[code]).find(([,translated])=>translated===source);
    if(match){const english=match[0];return language==="en"?english:(LANGUAGES[language][english]||english)}
  }
  return LANGUAGES[language]?.[source]||value;
}
function applyLanguage(root=document.body){
  if(!root)return;
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
  let node;
  while((node=walker.nextNode())){
    if(!node.data.trim())continue;
    if(!translationOriginals.has(node))translationOriginals.set(node,node.data);
    const original=translationOriginals.get(node);
    node.data=translateText(original);
  }
  const elements=[...(root.querySelectorAll?root.querySelectorAll("[placeholder],[title],[aria-label]"):[])];
  if(root.nodeType===Node.ELEMENT_NODE&&root.matches("[placeholder],[title],[aria-label]"))elements.unshift(root);
  for(const element of elements){
    let originals=translatedAttributes.get(element);
    if(!originals){originals={};translatedAttributes.set(element,originals)}
    for(const attribute of ["placeholder","title","aria-label"]){
      if(!element.hasAttribute(attribute))continue;
      if(!(attribute in originals))originals[attribute]=element.getAttribute(attribute);
      element.setAttribute(attribute,translateText(originals[attribute]));
    }
  }
  document.documentElement.lang=currentLanguage();
}
function setLanguage(language){
  if(!["en","ta","te"].includes(language))throw new Error("Unsupported language");
  localStorage.setItem("preferred_language",language);
  applyLanguage();
}
async function savePreferredLanguage(language){
  if(!["en","ta","te"].includes(language))throw new Error("Unsupported language");
  const user=getUser();
  if(user&&getToken()){
    const updated=await API.updateMe({preferred_language:language});
    localStorage.setItem("user",JSON.stringify(updated));
  }
  setLanguage(language);
  document.querySelectorAll("[data-language-select]").forEach(select=>{select.value=language});
}
document.addEventListener("DOMContentLoaded",()=>{
  applyLanguage();
  new MutationObserver(records=>records.forEach(record=>record.addedNodes.forEach(node=>{
    if(node.nodeType===Node.ELEMENT_NODE)applyLanguage(node);
    else if(node.nodeType===Node.TEXT_NODE&&node.data.trim()){
      if(!translationOriginals.has(node))translationOriginals.set(node,node.data);
      node.data=translateText(translationOriginals.get(node));
    }
  }))).observe(document.body,{childList:true,subtree:true});
});
function getToken(){return localStorage.getItem("access_token")}
function getUser(){const u=localStorage.getItem("user");return u?JSON.parse(u):null}
function setAuth(t,r,u){localStorage.setItem("access_token",t);localStorage.setItem("refresh_token",r);localStorage.setItem("user",JSON.stringify(u));setLanguage(u.preferred_language||currentLanguage())}
function clearAuth(){localStorage.removeItem("access_token");localStorage.removeItem("refresh_token");localStorage.removeItem("user")}
function requireAuth(){if(!getToken()){window.location.href="/login.html";return false}return true}
function dashboardUrl(user=getUser()){return user?.role==="admin"?"/admin/dashboard.html":"/workspace.html"}
function redirectIfLoggedIn(){const user=getUser();if(user)window.location.href=dashboardUrl(user)}
function logout(){clearAuth();window.location.href="/"}
function toQueryString(params={}){
  const sp=new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if(value === undefined || value === null || value === "") return;
    sp.append(key, String(value));
  });
  return sp.toString();
}

async function apiFetch(path,options={}){
  const token=getToken();
  const headers={"Content-Type":"application/json",...(options.headers||{})};
  if(token)headers["Authorization"]=`Bearer ${token}`;

  const method=(options.method||"GET").toUpperCase();
  const needsRefresh = ["POST","PUT","PATCH","DELETE"].includes(method);

  const res=await fetch(API_BASE+path,{...options,headers,cache:"no-store"});

  if(res.status===401){
    const rt=localStorage.getItem("refresh_token");
    if(rt){
      try{
        const rr=await fetch(API_BASE+"/auth/refresh",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({refresh_token:rt})});
        if(rr.ok){
          const rd=await rr.json();
          localStorage.setItem("access_token",rd.access_token);
          headers["Authorization"]=`Bearer ${rd.access_token}`;

          const retry=await fetch(API_BASE+path,{...options,headers});
          if(!retry.ok){
            const e=await retry.json().catch(()=>({}));
            throw new Error(e.detail||`Error ${retry.status}`);
          }
          if(retry.status===204){
            if(needsRefresh) triggerDashboardRefresh(method);
            return null;
          }
          const data=await retry.json();
          if(needsRefresh) triggerDashboardRefresh(method);
          return data;
        }else{
          const e=await rr.json().catch(()=>({}));
          throw new Error(e.detail||`Refresh failed (${rr.status})`);
        }
      }catch(e){
        showToast(e.message||"Session expired. Please login again","error");
      }
    }

    clearAuth();
    window.location.href="/login.html";
    return;
  }

  if(!res.ok){
    const err=await res.json().catch(()=>({}));
    throw new Error(err.detail||`Error ${res.status}`)
  }
  if(res.status===204){
    if(needsRefresh) triggerDashboardRefresh(method);
    return null;
  }
  const data=await res.json();
  if(needsRefresh) triggerDashboardRefresh(method);
  return data;
}

const API={
  register:(d)=>apiFetch("/auth/register",{method:"POST",body:JSON.stringify(d)}),
  login:(d)=>apiFetch("/auth/login",{method:"POST",body:JSON.stringify(d)}),
  logout:(d)=>apiFetch("/auth/logout",{method:"POST",body:JSON.stringify(d)}),
  logoutAll:()=>apiFetch("/auth/logout-all",{method:"POST"}),
  refresh:(rt)=>apiFetch("/auth/refresh",{method:"POST",body:JSON.stringify({refresh_token:rt})}),
  me:()=>apiFetch("/auth/me"),
  requestFarmerConversion:(terms_accepted)=>apiFetch("/auth/farmer-conversion/request",{method:"POST",body:JSON.stringify({terms_accepted})}),
  farmerConversionStatus:()=>apiFetch("/auth/farmer-conversion/status"),
  updateMe:(d)=>apiFetch("/auth/me",{method:"PUT",body:JSON.stringify(d)}),
  changePassword:(d)=>apiFetch("/auth/change-password",{method:"POST",body:JSON.stringify(d)}),
  forgotPassword:(email)=>apiFetch("/auth/forgot-password",{method:"POST",body:JSON.stringify({email})}),
  resetPassword:(d)=>apiFetch("/auth/reset-password",{method:"POST",body:JSON.stringify(d)}),
  sendVerification:()=>apiFetch("/auth/send-verification",{method:"POST"}),
  verifyPhone:(token)=>apiFetch("/auth/verify-phone",{method:"POST",body:JSON.stringify({verify_token:token})}),
  sessions:()=>apiFetch("/auth/sessions"),
  getUser:(id)=>apiFetch(`/auth/users/${id}`),
  createProduct:(d)=>apiFetch("/products/",{method:"POST",body:JSON.stringify(d)}),
  uploadProductImage: async (file)=>{
    const token=getToken();
    const form=new FormData();
    form.append("file",file);
    const headers={};
    if(token)headers["Authorization"]=`Bearer ${token}`;
    const res=await fetch(API_BASE+"/products/upload-image",{method:"POST",headers,body:form});
    if(!res.ok){const err=await res.json().catch(()=>({}));throw new Error(err.detail||`Error ${res.status}`)}
    return res.json();
  },
  listProducts:(p={})=>apiFetch("/products/?"+toQueryString(p)),
  recommendedProducts:(p={})=>apiFetch("/products/recommended?"+toQueryString(p)),
  getUserProducts:(id)=>apiFetch(`/products/?farmer_id=${id}&limit=100`),
  myProducts:()=>apiFetch("/products/my"),
  getProduct:(id)=>apiFetch(`/products/${id}`),
  updateProduct:(id,d)=>apiFetch(`/products/${id}`,{method:"PUT",body:JSON.stringify(d)}),
  deleteProduct:(id)=>apiFetch(`/products/${id}`,{method:"DELETE"}),
  createDemand:(d)=>apiFetch("/demands/",{method:"POST",body:JSON.stringify(d)}),
  listDemands:(p={})=>apiFetch("/demands/?"+new URLSearchParams(p)),
  myDemands:()=>apiFetch("/demands/my"),
  createOrder:(d)=>apiFetch("/orders/",{method:"POST",body:JSON.stringify(d)}),
  listOrders:()=>apiFetch("/orders/"),
  getOrder:(id)=>apiFetch(`/orders/${id}`),
  updateOrderStatus:(id,status,notes)=>apiFetch(`/orders/${id}/status`,{method:"PATCH",body:JSON.stringify({status,notes})}),
  createPayment:(order_id)=>apiFetch("/payments/create",{method:"POST",body:JSON.stringify({order_id})}),
  verifyPayment:(d)=>apiFetch("/payments/verify",{method:"POST",body:JSON.stringify(d)}),
  releaseEscrow:(order_id)=>apiFetch(`/payments/${order_id}/release-escrow`,{method:"POST"}),
  generateAgreement:(order_id)=>apiFetch(`/agreements/${order_id}/generate`,{method:"POST"}),
  signAgreement:(order_id)=>apiFetch(`/agreements/${order_id}/sign`,{method:"POST"}),
  getMessages:(order_id)=>apiFetch(`/chat/${order_id}/messages`),
  myChatRooms:()=>apiFetch("/chat/rooms/my"),
  createSupportTicket:(data)=>apiFetch("/support/tickets",{method:"POST",body:JSON.stringify(data)}),
  mySupportTickets:()=>apiFetch("/support/tickets/my"),
  getSupportTicket:(id)=>apiFetch(`/support/tickets/${id}`),
  replySupportTicket:(id,message)=>apiFetch(`/support/tickets/${id}/messages`,{method:"POST",body:JSON.stringify({message})}),
  matchForDemand:(id)=>apiFetch(`/match/products-for-demand/${id}`),
  matchForProduct:(id)=>apiFetch(`/match/demands-for-product/${id}`),
  createRating:(d)=>apiFetch("/ratings",{method:"POST",body:JSON.stringify(d)}),
  adminStats:()=>apiFetch("/admin/stats"),
  adminKpis:(range="today")=>apiFetch(`/admin/kpis?range=${encodeURIComponent(range)}`),
  adminRevenueSeries:(days=14)=>apiFetch(`/admin/analytics/revenue-series?days=${encodeURIComponent(days)}`),
  adminOrdersSeries:(days=14,status="")=>{
    const p=toQueryString({days,status:status||undefined});
    return apiFetch(`/admin/analytics/orders-series?${p}`);
  },
  adminTopProducts:(limit=10)=>apiFetch(`/admin/analytics/top-products?limit=${encodeURIComponent(limit)}`),
  adminSalesByCategory:(limit=10)=>apiFetch(`/admin/analytics/sales-by-category?limit=${encodeURIComponent(limit)}`),
  adminSalesByPaymentMethod:()=>apiFetch(`/admin/analytics/sales-by-payment-method`),
  adminListOrders:(p={})=>{
    return apiFetch(`/admin/orders?${toQueryString(p)}`);
  },
  adminSupportTickets:(status)=>apiFetch(`/support/admin/tickets?${toQueryString({status})}`),
  adminUpdateSupportTicket:(id,status)=>apiFetch(`/support/admin/tickets/${id}`,{method:"PATCH",body:JSON.stringify({status})}),
  // Backward-compat aliases (some pages may reference these)
  adminOrders: (p={})=>API.adminListOrders(p),

  adminListProducts:(p={})=>{
    return apiFetch(`/admin/products?${toQueryString(p)}`);
  },
  adminFarmerConversions:(status="pending")=>apiFetch(`/admin/farmer-conversions?status=${encodeURIComponent(status)}`),
  adminApproveFarmer:(id)=>apiFetch(`/admin/farmer-conversions/approve/${id}`,{method:"POST"}),
  adminApproveAllFarmers:(ids)=>apiFetch("/admin/farmer-conversions/approve-all",{method:"POST",body:JSON.stringify({user_ids:ids})}),
};


function showToast(msg,type="success"){
  let c=document.getElementById("toast-container");
  if(!c){c=document.createElement("div");c.id="toast-container";c.className="toast-container";document.body.appendChild(c)}
  const icons={success:"✅",error:"❌",info:"ℹ️"};
  const t=document.createElement("div");t.className=`toast ${type}`;t.innerHTML=`<span>${icons[type]}</span><span>${msg}</span>`;
  c.appendChild(t);setTimeout(()=>t.remove(),4000);
}

function triggerDashboardRefresh(reason = "status"){
  if (typeof window.refreshDashboardData === "function") {
    window.refreshDashboardData(reason);
    return;
  }
  if (window.location.pathname.includes("/workspace.html") || window.location.pathname.includes("/buyer/dashboard.html") || window.location.pathname.includes("/farmer/dashboard.html")) {
    window.location.reload();
  }
}

function startOrderStatusToastWatcher(){
  if(window.__orderStatusToastWatcherStarted) return;
  window.__orderStatusToastWatcherStarted = true;
  const statusText = {
    pending: "Order placed",
    accepted: "Order accepted",
    payment_pending: "Payment pending",
    paid: "Payment confirmed",
    in_transit: "Order dispatched",
    delivered: "Order delivered",
    completed: "Order completed",
    rejected: "Order rejected",
    cancelled: "Order cancelled",
    disputed: "Order disputed"
  };

  const check = async () => {
    try {
      const orders = await API.listOrders();
      const currentUser = getUser() || {};
      const snapshotKey = `agri_order_status_snapshot_${currentUser.id || "guest"}_${currentUser.role || "unknown"}`;
      const productSnapshotKey = `agri_product_stock_snapshot_${currentUser.id || "guest"}_${currentUser.role || "unknown"}`;
      const snapshot = JSON.parse(localStorage.getItem(snapshotKey) || "{}");
      const next = {};
      let changed = false;
      (orders || []).forEach(o => {
        next[o.id] = o.status;
        const prev = snapshot[o.id];
        if (o.farmer_id === currentUser.id && prev === undefined && o.status === "pending") {
          changed = true;
          showToast(`${o.order_number}: New order received`, "info");
        } else if (!prev && currentUser.role === "buyer" && ["accepted", "payment_pending"].includes(o.status)) {
          changed = true;
        } else if (prev && prev !== o.status) {
          changed = true;
          const label = statusText[o.status] || `Order moved to ${o.status.replace("_", " ")}`;
          showToast(`${o.order_number}: ${label}`, "info");
        }
      });
      localStorage.setItem(snapshotKey, JSON.stringify(next));

      try {
        const products = await API.listProducts({ limit: 200 });
        const productSnapshot = JSON.parse(localStorage.getItem(productSnapshotKey) || "{}");
        const productNext = {};
        (products || []).forEach(p => {
          const qty = Number(p.quantity_kg || 0);
          productNext[p.id] = qty;
          const prevQty = productSnapshot[p.id];
          if (prevQty !== undefined && Number(prevQty) !== qty) {
            changed = true;
            showToast(`${p.name}: stock updated to ${qty}kg`, "info");
          }
        });
        localStorage.setItem(productSnapshotKey, JSON.stringify(productNext));
      } catch (productError) {
        // ignore product snapshot errors
      }

      if (changed) {
        triggerDashboardRefresh("status-change");
      }
    } catch (e) {
      // ignore background polling failures
    }
  };

  check();
  setInterval(check, 8000);
}

function statusBadge(s){return`<span class="status status-${s}">${s.replace("_"," ")}</span>`}
function formatDate(d){if(!d)return"-";return new Date(d).toLocaleDateString("en-IN",{day:"numeric",month:"short",year:"numeric"})}
function escapeHtml(value){return String(value??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;")}
function formatChatTimestamp(value){
  if(!value)return"";
  const date=new Date(value);
  if(Number.isNaN(date.getTime()))return"";
  const now=new Date();
  if(date.toDateString()===now.toDateString())return date.toLocaleTimeString("en-IN",{hour:"numeric",minute:"2-digit"});
  return date.toLocaleDateString("en-IN",{day:"numeric",month:"short",...(date.getFullYear()===now.getFullYear()?{}:{year:"numeric"})});
}
function formatCurrency(n){return"₹"+Number(n).toLocaleString("en-IN",{minimumFractionDigits:2})}

// Convert a product's stored kg quantity into its displayed unit (gram/ton/kg)
function formatQty(p){
  const kg=Number(p?.quantity_kg)||0;
  const unit=(p?.quantity_unit||"kg").toLowerCase();
  if(unit==="gram"||unit==="g"){return trimNum(kg*1000)+" g"}
  if(unit==="ton"||unit==="tonne"||unit==="t"){return trimNum(kg/1000)+" ton"}
  return trimNum(kg)+" kg"
}
function trimNum(n){const r=Math.round(n*100)/100;return (Number.isInteger(r)?r:r.toFixed(2)).toLocaleString("en-IN")}

async function initiatePayment(order_id,onSuccess){
  try{
    const pd=await API.createPayment(order_id);
    if(pd.razorpay_order_id.startsWith("order_demo_")){
      showToast("Demo mode: simulating payment","info");
      await API.verifyPayment({razorpay_order_id:pd.razorpay_order_id,razorpay_payment_id:"demo_pay_"+Date.now(),razorpay_signature:"demo_sig"});
      showToast("Payment successful! 🎉","success");onSuccess&&onSuccess();return;
    }
    if(typeof Razorpay==="undefined"){
      throw new Error("Payment gateway could not be loaded. Please refresh the page and try again.");
    }
    new Razorpay({key:pd.key,amount:pd.amount,currency:pd.currency,name:"Agri Marketplace",description:`Order ${pd.order_number}`,order_id:pd.razorpay_order_id,
      handler:async(r)=>{try{await API.verifyPayment({razorpay_order_id:r.razorpay_order_id,razorpay_payment_id:r.razorpay_payment_id,razorpay_signature:r.razorpay_signature});showToast("Payment verified! Funds in escrow.","success");onSuccess&&onSuccess();}catch(e){showToast(e.message,"error");}},
      theme:{color:"#1a5c2a"}}).open();
  }catch(e){showToast(e.message,"error")}
}

function renderNavbar(){
  const user=getUser();
  const g=document.getElementById("guest-nav");
  const u=document.getElementById("user-nav");
  if(!user){if(g)g.style.display="flex";if(u)u.style.display="none";return}
  if(g)g.style.display="none";
  if(u){u.style.display="flex";const n=document.getElementById("nav-username");const a=document.getElementById("nav-avatar");if(n)n.textContent=user.full_name.split(" ")[0];if(a)a.textContent=user.full_name[0].toUpperCase()}
}
document.addEventListener("DOMContentLoaded",renderNavbar);
