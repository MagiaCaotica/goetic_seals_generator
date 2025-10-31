import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import io
import hashlib

# --- Constants and Configuration ---

HEBREW_MAP = {
    'A': 'א', 'B': 'ב', 'C': 'ג', 'D': 'ד', 'E': 'ה', 'F': 'ו', 'G': 'ז', 'H': 'ח', 'I': 'ט',
    'J': 'י', 'K': 'כ', 'L': 'ל', 'M': 'מ', 'N': 'נ', 'O': 'ס', 'P': 'ע', 'Q': 'פ', 'R': 'צ',
    'S': 'ק', 'T': 'ר', 'U': 'ש', 'V': 'ת', 'W': 'ך', 'X': 'ם', 'Y': 'ן', 'Z': 'ף'
}

ARABIC_MAP = {
    'A': 'أ', 'B': 'ب', 'C': 'ج', 'D': 'د', 'E': 'ه', 'F': 'و', 'G': 'ز', 'H': 'ح', 'I': 'ط',
    'J': 'ي', 'K': 'ك', 'L': 'ل', 'M': 'م', 'N': 'ن', 'O': 'س', 'P': 'ع', 'Q': 'ف', 'R': 'ص',
    'S': 'ق', 'T': 'ر', 'U': 'ش', 'V': 'ت', 'W': 'خ', 'X': 'م', 'Y': 'ن', 'Z': 'ظ'
}

LATIN_MAP = {chr(65+i): chr(65+i) for i in range(26)}

# Simplified phonetic mapping to Egyptian Hieroglyphs
EGYPTIAN_MAP = {
    'A': '𓄿', 'B': '𓃀', 'C': '𓎡', 'D': '𓂧', 'E': '𓇋', 'F': '𓆑', 'G': '𓎼', 'H': '𓉔',
    'I': '𓇋', 'J': '𓆓', 'K': '𓎡', 'L': '𓃭', 'M': '𓅓', 'N': '𓈖', 'O': '𓍱', 'P': '𓊪',
    'Q': '𓈎', 'R': '𓂋', 'S': '𓋴', 'T': '𓏏', 'U': '𓏲', 'V': '𓆑', 'W': '𓏲', 'X': '𓎡𓋴',
    'Y': '𓇋', 'Z': '𓊃'
}

CONVERSION_MAPS = {
    "Hebrew": HEBREW_MAP,
    "Arabic": ARABIC_MAP,
    "Latin": LATIN_MAP,
    "Egyptian": EGYPTIAN_MAP
}

RADIUS_OUTER = 1.0
RADIUS_INNER = 0.6
CIRCLE_CENTER = (0.0, 0.0)

# --- Font setup for special characters ---

def setup_egyptian_font():
    """
    Loads the local Egyptian Hieroglyphs font.
    Assumes the font file is in the same directory as the script.
    Returns the FontProperties object for matplotlib.
    """
    font_filename = "NotoSansEgyptianHieroglyphs-Regular.ttf"
    font_path = font_filename # Path is just the filename as it's in the same folder

    try:
        # Add font to matplotlib's font manager if it's not already aware of it
        # This is safer than just assuming it will find it.
        if font_path not in fm.findSystemFonts():
            fm.fontManager.addfont(font_path)
        
        # Create FontProperties object using the file path
        return fm.FontProperties(fname=font_path, size=24)
    except Exception:
        st.warning(f"Could not load font '{font_filename}'. Hieroglyphs will not be displayed. Make sure the file is in the same folder as the script.")
        return None

# --- Helper Functions ---

def get_seed_from_string(s: str) -> int:
    """Create a deterministic seed from a string."""
    return int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % (10**8)

def convert_text_to_sequence(text: str, lang_map: dict) -> tuple[str, list[int]]:
    """Convert input text to magical characters and a list of numerical indices."""
    processed_text = ''.join(filter(str.isalpha, text.upper()))
    magical_string = "".join([lang_map.get(char, '') for char in processed_text])
    
    # Use a simple 1-9 mapping for sigil points
    numerical_sequence = [(ord(char) - ord('A')) % 9 for char in processed_text if char in lang_map]
    
    return magical_string, numerical_sequence

def process_intent_for_mantra(text: str) -> str:
    """Remove vowels and duplicate letters for mantra-style sigils."""
    text = text.upper()
    vowels = "AEIOU"
    no_vowels = "".join([char for char in text if char.isalpha() and char not in vowels])
    seen = set()
    unique_chars = "".join([char for char in no_vowels if not (char in seen or seen.add(char))])
    return unique_chars
    
def draw_base_circles(ax, bg_color, line_color):
    """Draw the outer and inner circles."""
    ax.set_facecolor(bg_color)
    theta = np.linspace(0, 2 * np.pi, 200)
    
    # Outer circle
    x_outer = CIRCLE_CENTER[0] + RADIUS_OUTER * np.cos(theta)
    y_outer = CIRCLE_CENTER[1] + RADIUS_OUTER * np.sin(theta)
    ax.plot(x_outer, y_outer, color=line_color, linewidth=2)

    # Inner circle
    x_inner = CIRCLE_CENTER[0] + RADIUS_INNER * np.cos(theta)
    y_inner = CIRCLE_CENTER[1] + RADIUS_INNER * np.sin(theta)
    ax.plot(x_inner, y_inner, color=line_color, linewidth=1.5)

def draw_magical_characters(ax, magical_string: str, text_color: str, lang: str, **kwargs):
    """Place the magical characters around the ring."""
    if not magical_string:
        return
        
    char_angles = np.linspace(0, 2 * np.pi, len(magical_string), endpoint=False)
    text_radius = RADIUS_INNER + (RADIUS_OUTER - RADIUS_INNER) / 2
    
    egypt_font_prop = kwargs.get("egypt_font_prop")
    
    for char, angle in zip(magical_string, char_angles):
        x = CIRCLE_CENTER[0] + text_radius * np.cos(angle)
        y = CIRCLE_CENTER[1] + text_radius * np.sin(angle)
        # Rotation adjusted for better readability
        rotation = np.rad2deg(angle) - 90
        if 90 < rotation < 270:
            rotation -= 180
        
        if lang == "Egyptian" and egypt_font_prop:
            ax.text(x, y, char, color=text_color, ha='center', va='center', rotation=rotation, fontproperties=egypt_font_prop)
        else:
            ax.text(x, y, char, fontsize=24, color=text_color, ha='center', va='center', rotation=rotation)

def draw_wheel_sigil(ax, sequence: list[int], line_color: str, chaos_mode: bool, seed: int, wheel_base: str):
    """Draw the central sigil from the numerical sequence."""
    if not sequence:
        return

    # --- Define Wheel Bases: 9-Point circle and Planetary Kameas (Magic Squares) ---
    KAMEAS = {
        "Saturn": np.array([[4, 9, 2], [3, 5, 7], [8, 1, 6]]),
        "Jupiter": np.array([[4, 14, 15, 1], [9, 7, 6, 12], [5, 11, 10, 8], [16, 2, 3, 13]]),
        "Mars": np.array([[11, 24, 7, 20, 3], [4, 12, 25, 8, 16], [17, 5, 13, 21, 9], [10, 18, 1, 14, 22], [23, 6, 19, 2, 15]]),
        "Sun": np.array([[6, 32, 3, 34, 35, 1], [7, 11, 27, 28, 8, 30], [19, 14, 16, 15, 23, 24], [18, 20, 22, 21, 17, 13], [25, 29, 10, 9, 26, 12], [36, 5, 33, 4, 2, 31]]),
        "Venus": np.array([[22, 47, 16, 41, 10, 35, 4], [5, 23, 48, 17, 42, 11, 29], [30, 6, 24, 49, 18, 36, 12], [13, 31, 7, 25, 43, 19, 37], [38, 14, 32, 1, 26, 44, 20], [21, 39, 8, 33, 2, 27, 45], [46, 15, 40, 9, 34, 3, 28]]),
        "Mercury": np.array([[8, 58, 59, 5, 4, 62, 63, 1], [49, 15, 14, 52, 53, 11, 10, 56], [41, 23, 22, 44, 45, 19, 18, 48], [32, 34, 35, 29, 28, 38, 39, 25], [40, 26, 27, 37, 36, 30, 31, 33], [17, 47, 46, 20, 21, 43, 42, 24], [9, 55, 54, 12, 13, 51, 50, 16], [64, 2, 3, 61, 60, 6, 7, 57]]),
        "Moon": np.array([[37, 78, 29, 70, 21, 62, 13, 54, 5], [6, 38, 79, 30, 71, 22, 63, 14, 46], [47, 7, 39, 80, 31, 72, 23, 55, 15], [16, 48, 8, 40, 81, 32, 64, 24, 56], [57, 17, 49, 9, 41, 73, 33, 65, 25], [26, 58, 18, 50, 1, 42, 74, 34, 66], [67, 27, 59, 10, 51, 2, 43, 75, 35], [36, 68, 19, 60, 11, 52, 3, 44, 76], [77, 28, 69, 20, 61, 12, 53, 4, 45]])
    }

    path_points = []
    if wheel_base == "9-Point Wheel":
        # 9 points on a circle for the sigil wheel
        sigil_points_angles = np.linspace(0, 2 * np.pi, 9, endpoint=False)
        sigil_radius = RADIUS_INNER * 0.85

        if chaos_mode:
            rng = np.random.default_rng(seed)
            sigil_points_angles = rng.permutation(sigil_points_angles)

        sigil_wheel_points = [
            (CIRCLE_CENTER[0] + sigil_radius * np.cos(a), CIRCLE_CENTER[1] + sigil_radius * np.sin(a))
            for a in sigil_points_angles
        ]
        
        # Draw the points of the wheel for context, but subtly
        # ax.scatter([p[0] for p in sigil_wheel_points], [p[1] for p in sigil_wheel_points], s=20, color=line_color, alpha=0.3)

        path_points = [sigil_wheel_points[i] for i in sequence]
    else: # It's a planetary kamea
        kamea = KAMEAS[wheel_base]
        size = kamea.shape[0]
        # Create a grid of points inside the inner circle
        coords = np.linspace(-RADIUS_INNER * 0.7, RADIUS_INNER * 0.7, size)
        xx, yy = np.meshgrid(coords, coords)
        point_map = {kamea[i, j]: (xx[i, j], yy[i, j]) for i in range(size) for j in range(size)}
        
        # Reduce the sequence numbers to be within the kamea's range
        reduced_sequence = [(num % (size*size)) + 1 for num in sequence]
        path_points = [point_map[num] for num in reduced_sequence if num in point_map]

        # Draw the grid points for context, but subtly
        # ax.scatter(xx, yy, s=10, color=line_color, alpha=0.2)

    if not path_points:
        return

    # Draw lines connecting the points in sequence
    for i in range(len(path_points) - 1):
        p1 = path_points[i]
        p2 = path_points[i+1]
        # Avoid drawing line if points are the same
        if p1 != p2:
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=line_color, linewidth=2.5, solid_capstyle='round')

    # Mark start and end points
    start_point = path_points[0]
    end_point = path_points[-1]

    # Start with a small circle
    ax.add_patch(plt.Circle(start_point, 0.035, color=line_color, fill=False, linewidth=2))

    # End with a small perpendicular line
    if len(path_points) > 1:
        p_before_end = path_points[-2]
        dx = end_point[0] - p_before_end[0]
        dy = end_point[1] - p_before_end[1]
        angle = np.arctan2(dy, dx)
        perp_angle = angle + np.pi / 2
        end_bar_len = 0.03
        x1 = end_point[0] + end_bar_len * np.cos(perp_angle)
        y1 = end_point[1] + end_bar_len * np.sin(perp_angle)
        x2 = end_point[0] - end_bar_len * np.cos(perp_angle)
        y2 = end_point[1] - end_bar_len * np.sin(perp_angle)
        ax.plot([x1, x2], [y1, y2], color=line_color, linewidth=2.5, solid_capstyle='round')

def draw_mantra_sigil(ax, text: str, line_color: str, lang: str, **kwargs):
    """Draw a sigil by overlaying characters."""
    if not text:
        return
    
    egypt_font_prop = kwargs.get("egypt_font_prop")

    for char in text:
        if lang == "Egyptian" and egypt_font_prop:
            # Create a new FontProperties object with a larger size for the mantra
            mantra_font_prop = fm.FontProperties(fname=egypt_font_prop.get_file(), size=150)
            ax.text(0, 0, char, color=line_color, ha='center', va='center', alpha=0.5, fontproperties=mantra_font_prop)
        else:
            ax.text(0, 0, char, color=line_color, ha='center', va='center', alpha=0.5, fontsize=150, family='sans-serif')

def create_seal_figure(bg_color, line_color, **kwargs):
    """Generate the entire seal figure."""
    fig, ax = plt.subplots(figsize=(8, 8), facecolor=bg_color)
    
    draw_base_circles(ax, bg_color, line_color)
    
    if kwargs.get("method") == "Wheel Method":
        draw_magical_characters(
            ax,
            magical_string=kwargs["magical_string"],
            text_color=line_color,
            lang=kwargs["lang"],
            egypt_font_prop=kwargs.get("egypt_font_prop")
        )
        draw_wheel_sigil(ax, kwargs["numerical_sequence"], line_color, kwargs["chaos_mode"], kwargs["seed"], kwargs["wheel_base"])
    elif kwargs.get("method") == "Graphic Mantra":
        draw_magical_characters(
            ax,
            magical_string=kwargs["magical_string"],
            text_color=line_color,
            lang=kwargs["lang"],
            egypt_font_prop=kwargs.get("egypt_font_prop")
        )
        draw_mantra_sigil(ax, text=kwargs["mantra_text"], line_color=line_color, lang=kwargs["lang"], egypt_font_prop=kwargs.get("egypt_font_prop"))

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.axis('off')
    plt.tight_layout()
    
    return fig

def sanitize_filename(name: str) -> str:
    """Create a clean filename from a string."""
    return "".join(c for c in name.replace(" ", "_") if c.isalnum() or c == "_").lower()

# --- Streamlit UI ---

def main():
    st.set_page_config(page_title="Sigil Generator", layout="wide")

    # Inyectar CSS para hacer las imágenes de matplotlib responsivas
    st.markdown("""
        <style>
        /* Esto hace que la imagen generada por st.pyplot se ajuste al contenedor */
        img {
            max-width: 100%;
            height: auto;
        }
        /* Opcional: Centrar la imagen del sello */
        .stPlotlyChart, .stImage {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("Magickal Sigil Generator")
    st.markdown(
        """
        *A tool for the crystallization of Will.*
        **Author:** cha0smagick, the Techno-Mage. For [Chaos Magic](https://grimoriomagiadelcaos.blogspot.com).
        
        ---
        **Telegram Community:**
        - **News Channel:** [Magia Caótica](https://t.me/magiacaotica)
        - **Discussion Group:** [Chaos Magic Coven](https://t.me/magiacaoticacoven)
        """
    )

    # --- Setup ---
    egypt_font_prop = setup_egyptian_font()

    # --- Sidebar for Controls ---
    st.sidebar.header("Control Panel")
    intent_text = st.sidebar.text_input("Enter your Intent, Name, or Desire:", "MY DESIRE")
    
    sigil_method = st.sidebar.selectbox("1. Choose a Sigilization Method:", ["Wheel Method", "Graphic Mantra"], key="sigil_method")
    
    conversion_lang = st.sidebar.selectbox("2. Choose a Magickal Alphabet:", list(CONVERSION_MAPS.keys()))

    wheel_base = "9-Point Wheel"
    process_text = True # Default for mantra

    if sigil_method == "Wheel Method":
        with st.sidebar.expander("Method Options: Wheel & Planetary Kameas", expanded=True):
            wheel_base_options = ["9-Point Wheel", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
            wheel_base = st.selectbox("Choose a Base for the Sigil:", wheel_base_options, help="Use a simple 9-point wheel or a traditional planetary magic square (Kamea) to imbue your sigil with specific energies.")
            chaos_mode = st.checkbox("Activate Chaos Mode", help="For the 9-Point Wheel, this randomly permutes the points for a more unpredictable creation. The same intent will still produce the same chaotic sigil.")
    
    elif sigil_method == "Graphic Mantra":
        with st.sidebar.expander("Method Options: Graphic Mantra", expanded=True):
            process_text = st.checkbox("Remove vowels & duplicates", True, help="Condenses the intent to its essence by removing vowels and repeated letters, a classic sigilization method.")
        chaos_mode = False # Not applicable
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("3. Aesthetic Customization")
    bg_color = st.sidebar.color_picker("Background Color", "#000000")
    line_color = st.sidebar.color_picker("Sigil Color", "#FFFFFF")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Support this Tool")
    st.sidebar.markdown("If you find this generator useful, consider making a donation in cryptocurrency. Your support helps maintain and improve this project.")
    st.sidebar.markdown("**Bitcoin (BTC):**")
    st.sidebar.code("154P7GdFHBH2N5XuSauBhEbdGYSen8RkBT")
    st.sidebar.markdown("**Dogecoin (DOGE):**")
    st.sidebar.code("DFT2oi1gsWFKiqqDhPabTud9NN6M2EbzhY")

    st.sidebar.markdown("---")
    st.sidebar.markdown("Or donate via PayPal:")
    paypal_button_html = f"""
    <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=alekos200@yahoo.es&item_name=Donation+for+Magickal+Sigil+Generator&currency_code=EUR" target="_blank" rel="noopener noreferrer">
        <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="Donate with PayPal button">
    </a>
    """
    st.sidebar.markdown(paypal_button_html, unsafe_allow_html=True)



    # --- Main Area for Display ---
    if intent_text:
        lang_map = CONVERSION_MAPS[conversion_lang]
        
        # Generate a stable seed from the original, unprocessed intent
        seed = get_seed_from_string(intent_text)
        
        # Prepare arguments for drawing functions
        fig_args = {
            "bg_color": bg_color,
            "line_color": line_color,
            "method": sigil_method,
            "lang": conversion_lang,
            "seed": seed,
            "chaos_mode": chaos_mode,
            "egypt_font_prop": egypt_font_prop,
            "wheel_base": wheel_base
        }

        if sigil_method == "Wheel Method":
            magical_string, numerical_sequence = convert_text_to_sequence(intent_text, lang_map)
            fig_args["magical_string"] = magical_string
            fig_args["numerical_sequence"] = numerical_sequence
        elif sigil_method == "Graphic Mantra":
            base_text = process_intent_for_mantra(intent_text) if process_text else ''.join(filter(str.isalpha, intent_text.upper()))
            magical_string, _ = convert_text_to_sequence(intent_text, lang_map) # For the outer ring
            mantra_text = "".join([lang_map.get(char, '') for char in base_text])
            fig_args["magical_string"] = magical_string
            fig_args["mantra_text"] = mantra_text

        # --- Display Area (sin columnas para ser responsivo) ---

        # Sección de la imagen del sello
        st.subheader("Generated Sigil")
        try:
            fig = create_seal_figure(**fig_args)
            
            # Display the image. El CSS inyectado arriba se encargará de que sea responsiva.
            st.pyplot(fig)

        except Exception as e:
            st.error(f"An error occurred while generating the sigil: {e}")
            # Si hay un error, no continuamos a las siguientes secciones
            st.stop()

        # Sección de detalles del proceso
        with st.expander("Show Processed Intent & Details", expanded=True):
            st.markdown(f"**Method:** `{sigil_method}`")
            st.markdown(f"**Alphabet:** `{conversion_lang}`")
            st.markdown(f"**Magickal String (Ring):**")
            text_align = "right" if conversion_lang in ["Hebrew", "Arabic"] else "left"
            direction = "rtl" if conversion_lang in ["Hebrew", "Arabic"] else "ltr"
            st.markdown(f"<p style='font-size: 24px; direction: {direction}; text-align: {text_align};'>{fig_args.get('magical_string', '')}</p>", unsafe_allow_html=True)
            st.markdown(f"**Numeric Seed:** `{seed}`")
            if sigil_method == "Wheel Method":
                if wheel_base == "9-Point Wheel":
                    st.info("The sigil is generated by connecting points on a 9-point wheel.")
                else:
                    st.info(f"The sigil is drawn on the Kamea (Magic Square) of **{wheel_base}**.")
            elif sigil_method == "Graphic Mantra":
                st.info("The sigil is generated by overlaying the letters of the processed intent.")
                st.markdown(f"**Letters for Mantra:** `{fig_args.get('mantra_text', '')}`")

        # Sección de descarga
        st.subheader("Download Sigil")
        clean_filename = sanitize_filename(intent_text[:20])
        
        # SVG Download
        svg_buffer = io.StringIO()
        fig.savefig(svg_buffer, format='svg', transparent=True, bbox_inches='tight', pad_inches=0.1)
        st.download_button(
            label="Download as SVG (Vector)",
            data=svg_buffer.getvalue(),
            file_name=f"sello_{clean_filename}.svg",
            mime="image/svg+xml",
        )

        # PNG Download
        png_buffer = io.BytesIO()
        fig.savefig(png_buffer, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        st.download_button(
            label="Download as PNG (High Quality)",
            data=png_buffer.getvalue(),
            file_name=f"sello_{clean_filename}.png",
            mime="image/png",
        )

    else:
        st.info("Enter an intent in the left panel to begin forging your sigil.")

if __name__ == '__main__':
    main()
