import streamlit as st
import streamlit.components.v1 as components
import pymupdf
import base64
import requests
import os

# --- 1. Cross-Device Screen Optimization ---
st.set_page_config(page_title="Official Magazine Launch", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding: 0rem !important; 
            max-width: 100% !important; 
            width: 100% !important;
        }
        iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

if 'reader_active' not in st.session_state:
    st.session_state.reader_active = False
if 'html_content' not in st.session_state:
    st.session_state.html_content = ""

# Cache the audio download so the app remains fast on subsequent loads
@st.cache_data
def fetch_sangeet_audio():
    audio_url = "https://upload.wikimedia.org/wikipedia/commons/transcoded/7/74/Sitar_and_Tabla.ogg/Sitar_and_Tabla.ogg.mp3"
    try:
        # Download the audio file directly into the server's memory
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(audio_url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Convert the raw MP3 into a Base64 string to embed directly into HTML
            encoded_audio = base64.b64encode(response.content).decode("utf-8")
            return f"data:audio/mpeg;base64,{encoded_audio}"
    except Exception as e:
        print(f"Failed to fetch audio locally: {e}")
    # Fallback to standard URL if download fails
    return audio_url

def generate_production_launch_book(pdf_path, audio_src):
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    page0 = doc.load_page(0)
    ratio = page0.rect.height / page0.rect.width
    
    # Memory optimization
    if total_pages > 100:
        mat = pymupdf.Matrix(0.9, 0.9)
        jpg_qual = 55
    elif total_pages > 50:
        mat = pymupdf.Matrix(1.1, 1.1)
        jpg_qual = 65
    else:
        mat = pymupdf.Matrix(1.5, 1.5)
        jpg_qual = 80
        
    images_html = ""
    progress_bar = st.progress(0, text=f"Rendering {total_pages} pages for virtual inauguration...")
    
    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_data = pix.tobytes("jpeg", jpg_quality=jpg_qual)
        b64_img = base64.b64encode(img_data).decode("utf-8")
        
        css_class = "page"
        if page_num == 0 or page_num == total_pages - 1:
            css_class = "page page-cover"
            
        images_html += f"""
        <div class="{css_class}">
            <img src="data:image/jpeg;base64,{b64_img}">
        </div>
        """
        progress_bar.progress((page_num + 1) / total_pages)
        
    progress_bar.empty()
    
    # --- HTML: PURE EMBEDDED AUDIO & TOUCH RESPONSIVE ENGINE ---
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="https://cdn.jsdelivr.net/npm/page-flip/dist/js/page-flip.browser.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <style>
            body {{
                background: linear-gradient(135deg, #1f1f1f 0%, #0a0a0a 100%);
                margin: 0; display: flex; justify-content: center; align-items: center;
                height: 100vh; width: 100vw; overflow: hidden;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                touch-action: none;
            }}
            
            #book-wrapper {{
                display: flex; justify-content: center; align-items: center;
                width: 100%; height: 100%;
            }}
            #book {{ box-shadow: 0 25px 60px rgba(0,0,0,0.9); }}
            .page {{ background-color: #faf9f6; overflow: hidden; }}
            .page img {{ width: 100%; height: 100%; object-fit: fill; }}
            .page::after {{
                content: ''; position: absolute; top: 0; bottom: 0; left: 0; width: 35px;
                background: linear-gradient(to right, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0) 100%);
                z-index: 10; pointer-events: none;
            }}
            .page-cover {{ background-color: #111; border: 1px solid #333; }}
            .page-cover::after {{ display: none; }}

            /* --- LAUNCH STAGE --- */
            #launch-overlay {{
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: radial-gradient(circle, #1a1a1a 0%, #000000 100%);
                z-index: 9999; display: flex; flex-direction: column;
                justify-content: center; align-items: center;
                transition: opacity 1.5s ease-in-out;
            }}
            .launch-logo {{
                width: 120px; margin-bottom: 20px;
                filter: drop-shadow(0px 4px 10px rgba(212, 175, 55, 0.4));
            }}
            .launch-title {{
                color: #d4af37; font-size: clamp(2rem, 5vw, 3.5rem);
                text-transform: uppercase; letter-spacing: 4px;
                margin-bottom: 10px; text-align: center;
                text-shadow: 0px 4px 15px rgba(212, 175, 55, 0.4); margin-top: 0;
            }}
            .launch-subtitle {{
                color: #ffffff; font-size: clamp(1rem, 3vw, 1.5rem);
                margin-bottom: 40px; text-align: center; font-weight: 300;
            }}
            
            .ribbon-container {{
                position: relative; width: 100%; height: 120px;
                display: flex; justify-content: center; align-items: center;
                cursor: none; 
            }}
            
            .ribbon-half {{
                width: 50%; height: 80px;
                background: linear-gradient(to bottom, #d32f2f, #9a0007);
                box-shadow: 0 10px 20px rgba(0,0,0,0.5);
                transition: transform 2s cubic-bezier(0.25, 1, 0.5, 1);
                display: flex; align-items: center;
            }}
            .ribbon-left {{ border-right: 3px dashed #ffd700; justify-content: flex-end; }}
            .ribbon-right {{ border-left: 3px dashed #ffd700; justify-content: flex-start; }}
            
            #scissors {{
                position: absolute; font-size: 5rem;
                pointer-events: none; transition: transform 0.1s;
                z-index: 10000; text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
            }}
            .snip {{ transform: rotate(-45deg) scale(0.8); }}
            .cut-left {{ transform: translateX(-100vw); }}
            .cut-right {{ transform: translateX(100vw); }}
            
            .launch-footer {{
                position: absolute; bottom: 30px; color: #888;
                font-size: clamp(0.8rem, 2vw, 1.2rem); letter-spacing: 2px; text-align: center; padding: 0 10px;
            }}
        </style>
    </head>
    <body>
        
        <!-- FULLY EMBEDDED AUDIO (Bypasses Browser Network Restrictions) -->
        <audio id="bhartiya-sangeet" loop preload="auto">
            <source src="{audio_src}" type="audio/mpeg">
        </audio>

        <div id="launch-overlay">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" class="launch-logo" alt="State Emblem of India">
            <h1 class="launch-title">Official Launch</h1>
            <div class="launch-subtitle">Nutan Pratibimb 2026</div>
            <div class="ribbon-container" id="ribbon-box">
                <div class="ribbon-half ribbon-left" id="r-left"></div>
                <div class="ribbon-half ribbon-right" id="r-right"></div>
                <div id="scissors">✂️</div>
            </div>
            <div class="launch-footer">Inaugurated by Shri P.C. Mody, Secretary-General, Rajya Sabha</div>
        </div>

        <div id="book-wrapper">
            <div id="book">
                {images_html}
            </div>
        </div>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                
                // 1. MOBILE RESPONSIVE ENGINE
                setTimeout(() => {{
                    const ratio = {ratio}; 
                    let screenW = window.innerWidth * 0.95;
                    let screenH = window.innerHeight * 0.95;
                    
                    const isMobile = window.innerWidth < 768;
                    
                    let bookW = screenW;
                    let bookH = isMobile ? (bookW * ratio) : (bookW * (ratio / 2));
                    
                    if (bookH > screenH) {{
                        bookH = screenH;
                        bookW = isMobile ? (bookH / ratio) : (bookH / (ratio / 2));
                    }}
                    
                    const pageFlip = new St.PageFlip(document.getElementById('book'), {{
                        width: isMobile ? bookW : (bookW / 2), 
                        height: bookH,
                        size: "fixed",
                        usePortrait: isMobile,           
                        drawShadow: true,                
                        showCover: true,                 
                        flippingTime: 1100,              
                        maxShadowOpacity: 0.7,
                        mobileScrollSupport: true        
                    }});
                    pageFlip.loadFromHTML(document.querySelectorAll('.page'));
                    
                    document.addEventListener('keydown', (e) => {{
                        if (e.key === 'ArrowRight') pageFlip.flipNext();
                        if (e.key === 'ArrowLeft') pageFlip.flipPrev();
                    }});
                }}, 300);

                // 2. TOUCH & MOUSE RIBBON CUTTING
                const ribbonBox = document.getElementById('ribbon-box');
                const scissors = document.getElementById('scissors');
                const overlay = document.getElementById('launch-overlay');
                let isCut = false;

                function moveScissors(e) {{
                    if(isCut) return;
                    const rect = ribbonBox.getBoundingClientRect();
                    let clientX = e.clientX;
                    let clientY = e.clientY;
                    
                    if (e.touches && e.touches.length > 0) {{
                        clientX = e.touches[0].clientX;
                        clientY = e.touches[0].clientY;
                    }}
                    
                    scissors.style.left = (clientX - rect.left - 40) + 'px';
                    scissors.style.top = (clientY - rect.top - 40) + 'px';
                }}

                ribbonBox.addEventListener('mousemove', moveScissors);
                ribbonBox.addEventListener('touchmove', moveScissors);
                ribbonBox.addEventListener('touchstart', moveScissors);

                function cutRibbon(e) {{
                    if(isCut) return;
                    isCut = true;
                    
                    // --- TRIGGER THE AUDIO SYNCHRONOUSLY ---
                    // By executing this instantly upon the click gesture, browsers guarantee playback
                    const sangeet = document.getElementById('bhartiya-sangeet');
                    sangeet.volume = 0.6;
                    sangeet.play().catch(err => console.error("Audio playback error:", err));
                    
                    scissors.classList.add('snip');
                    
                    setTimeout(() => {{
                        document.getElementById('r-left').classList.add('cut-left');
                        document.getElementById('r-right').classList.add('cut-right');
                        scissors.style.opacity = '0'; 
                    }}, 200);

                    setTimeout(() => {{
                        var end = Date.now() + (4 * 1000);
                        var defaults = {{ startVelocity: 45, spread: 360, ticks: 60, zIndex: 999999 }};
                        var interval = setInterval(function() {{
                            var timeLeft = end - Date.now();
                            if (timeLeft <= 0) return clearInterval(interval);
                            var particleCount = 50 * (timeLeft / (4*1000));
                            confetti(Object.assign({{}}, defaults, {{ particleCount, origin: {{ x: Math.random() * (0.3 - 0.1) + 0.1, y: Math.random() - 0.2 }} }}));
                            confetti(Object.assign({{}}, defaults, {{ particleCount, origin: {{ x: Math.random() * (0.9 - 0.7) + 0.7, y: Math.random() - 0.2 }} }}));
                        }}, 250);
                    }}, 400);

                    setTimeout(() => {{
                        overlay.style.opacity = '0';
                        setTimeout(() => {{ overlay.style.display = 'none'; }}, 1500);
                    }}, 1500);
                }}

                // Bind to explicit user gestures
                ribbonBox.addEventListener('click', cutRibbon);
                ribbonBox.addEventListener('touchend', cutRibbon);
            }});
        </script>
    </body>
    </html>
    """
    return html

# --- Main Interface ---
if not st.session_state.reader_active:
    st.markdown("<br><br><br><h1 style='text-align: center; font-size: clamp(2rem, 4vw, 3.5rem);'>🏛️ Virtual Inauguration Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #888;'>Official Launch of Nutan Pratibimb 2026</p><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 INITIATE LAUNCH SEQUENCE", type="primary", use_container_width=True):
            with st.spinner("Preparing official launch environment and downloading Sangeet..."):
                try:
                    # 1. Fetch the audio first
                    audio_source = fetch_sangeet_audio()
                    # 2. Inject it into the book
                    st.session_state.html_content = generate_production_launch_book("NUTAN PRATIBIMB 2026.pdf", audio_source)
                    st.session_state.reader_active = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load document. Make sure 'NUTAN PRATIBIMB 2026.pdf' is in the GitHub folder. Error: {e}")

else:
    components.html(st.session_state.html_content, width=None, height=900, scrolling=False)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("❌ End Session", use_container_width=True):
            st.session_state.reader_active = False
            st.session_state.html_content = ""
            st.rerun()
