import streamlit as st

# Use experimental query param API
query_params = st.query_params
page = query_params.get("page", "home")

# --- Sample data (trimmed for readability, but apply the same structure to all books) ---
genres = {
    "Philosophy": [
        {
            "title": "BEING AND TIME",
            "image": "https://m.media-amazon.com/images/I/91VWC7ydAbL._AC_UF1000,1000_QL80_.jpg",
            "Description": "A profound exploration of existence, time, and human experience—Heidegger challenges us to rethink the nature of being itself. This philosophical masterpiece redefines how we understand consciousness and mortality."
        },
        {
            "title": "The Republic",
            "image": "https://m.media-amazon.com/images/I/91MRDNc-mIL._UF1000,1000_QL80_.jpg",
            "Description": "Plato’s classic dialogue on justice, society, and governance explores philosophical ideals through conversations. It remains essential reading for anyone interested in truth, morality, and political thought."
        },
        {
            "title": "The Art of War",
            "image": "https://m.media-amazon.com/images/I/71jWgemHbML._AC_UF1000,1000_QL80_.jpg",
            "Description": "Ancient wisdom on conflict, leadership, and strategy—Sun Tzu offers powerful lessons on discipline, foresight, and victory, showing how battles are won not by strength, but by intellect and timing."
        },
        {
            "title": "The Myth of Sisyphus",
            "image": "https://ritikart.com/cdn/shop/files/1_88148006-517a-4532-b9c7-41471341b746.jpg?v=1697449196",
            "Description": "Camus explores the absurd condition of human existence and how we respond to its meaninglessness. He urges us to embrace life with courage, defiance, and a sense of personal freedom."
        },
        {
            "title": "LETTERS",
            "image": "https://m.media-amazon.com/images/I/7179cgoWCXL._AC_UF1000,1000_QL80_.jpg",
            "Description": "Seneca’s deeply personal letters share insights on living virtuously, practicing reason, and embracing adversity with resilience. His timeless wisdom encourages reflection, self-discipline, and finding peace through Stoic philosophy."
        },
        {
            "title": "Critique of Pure Reason",
            "image": "https://m.media-amazon.com/images/I/81mgweej4pL._UF1000,1000_QL80_.jpg",
            "Description": "Kant’s groundbreaking work challenges how we acquire knowledge, blending reason and perception. He reshapes Western thought by questioning how we understand reality, shaping modern epistemology and metaphysical inquiry."
        },
    ],
    "Self Help": [
        {
            "title": "Atomic Habits",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkb50Lzxld9H-fbdRvV9KVPIgux6IMbR3I7A&s",
            "Description": "Master the science of habit-building with practical strategies. James Clear teaches how tiny changes compound into powerful transformations, helping you break bad habits and create a life of consistent growth."
        },
        {
            "title": "The Power of Now",
            "image": "https://m.media-amazon.com/images/I/61Ij8nLooNL._UF1000,1000_QL80_.jpg",
            "Description": "Eckhart Tolle guides readers toward inner peace by letting go of past regrets and future anxieties. This spiritual manual shows how presence and mindfulness can lead to lasting transformation."
        },
        {
            "title": "Deep Work",
            "image": "https://m.media-amazon.com/images/I/81JJ7fyyKyS.jpg",
            "Description": "Cal Newport introduces the concept of deep work—focused, undistracted productivity in a distracted world. Learn how to reclaim focus, enhance cognitive abilities, and achieve meaningful success in a digital age."
        },
        {
            "title": "Meditations",
            "image": "https://images-cdn.ubuy.co.in/66be6bd6a9f2fb3ac92fa66b-marcus-aurelius-meditations-adapted.jpg",
            "Description": "Marcus Aurelius’s private thoughts reveal Stoic principles for resilience, self-mastery, and virtue. This timeless work teaches how to lead with integrity and find calm amidst chaos and adversity."
        },
        {
            "title": "Man’s Search for Meaning",
            "image": "https://charliebyrne.ie/wp-content/uploads/2023/02/9781844132393-255x315.jpg",
            "Description": "Viktor Frankl’s memoir recounts his survival in Nazi concentration camps and introduces logotherapy. He explores how finding meaning in suffering can lead to spiritual resilience and enduring hope."
        },
        {
            "title": "The Courage to Be Disliked",
            "image": "https://m.media-amazon.com/images/I/71TZnQSik3L._AC_UF1000,1000_QL80_.jpg",
            "Description": "Through a philosophical dialogue, this book empowers readers to break free from social pressures. Learn how to live authentically, reject approval-seeking, and find true freedom and self-worth."
        },
    ],
    "Science & Tech": [
        {
            "title": "Professor Calculus: Science's Forgotten Genius",
            "image": "https://m.media-amazon.com/images/I/717bFyLpEYL._AC_UF1000,1000_QL80_.jpg",
            "Description": "A humorous homage to Tintin’s fictional scientist, this book mixes fun and fact to celebrate creativity, curiosity, and quirky brilliance in science through a nostalgic, light-hearted narrative."
        },
        {
            "title": "INVENTIONS AND DISCOVERIES",
            "image": "https://m.media-amazon.com/images/I/91+5U0bxlML.jpg",
            "Description": "A fascinating dive into the breakthroughs that changed the world. This book chronicles human innovation—from the wheel to the internet—highlighting how creativity and perseverance drive human progress."
        },
        {
            "title": "THE TIME MACHINE",
            "image": "https://m.media-amazon.com/images/I/81BWWw8+sCL._AC_UF1000,1000_QL80_.jpg",
            "Description": "H.G. Wells imagines a future shaped by time travel, social decay, and evolution. This classic sci-fi novel warns of technological power and poses questions about humanity’s ultimate destiny."
        },
        {
            "title": "Brief Answers to the Big Questions",
            "image": "https://m.media-amazon.com/images/I/71E8sYS9j4L._AC_UF1000,1000_QL80_.jpg",
            "Description": "Stephen Hawking tackles life’s greatest mysteries—from black holes to AI. This final work challenges readers to think about the future, human survival, and the search for cosmic meaning."
        },
        {
            "title": "Astrophysics for People in a Hurry",
            "image": "https://m.media-amazon.com/images/I/914EiU2QImL.jpg",
            "Description": "Neil deGrasse Tyson presents complex astrophysical concepts in an accessible, witty way. Discover how the universe works, from dark matter to quantum particles, all in bite-sized, digestible chapters."
        },
        {
            "title": "THE THREE BODY PROBLEM",
            "image": "https://m.media-amazon.com/images/M/MV5BMDdkYWZiZWYtMzA0Yi00NzNlLThkODktY2Q3N2NjN2ExZmMwXkEyXkFqcGc@._V1_.jpg",
            "Description": "A mind-bending sci-fi tale about first contact with an alien race. This novel blends physics, philosophy, and political intrigue in a sweeping saga of interstellar conflict and survival."
        },
    ],
    "Entrepreneurship": [
        {
            "title": "Zero to One",
            "image": "https://upload.wikimedia.org/wikipedia/en/d/d3/Zero_to_One.jpg",
            "Description": "Peter Thiel shares bold ideas for creating innovation from nothing. This startup manual encourages founders to build unique solutions that define new markets and drive long-term technological progress."
        },
        {
            "title": "THE DIARY OF A CEO",
            "image": "https://m.media-amazon.com/images/I/61PIpidSThL.jpg",
            "Description": "Steven Bartlett outlines 33 powerful life and business principles. Through vulnerability and insight, he shares how mindset shifts, discipline, and self-awareness can fuel growth and sustainable success."
        },
        {
            "title": "The Lean Startup",
            "image": "https://m.media-amazon.com/images/I/71sxTeZIi6L._AC_UF1000,1000_QL80_.jpg",
            "Description": "Eric Ries revolutionizes how businesses are built—teaching how to test ideas, pivot quickly, and avoid failure. A practical guide to building adaptable, resilient startups through rapid experimentation."
        },
        {
            "title": "Shoe Dog",
            "image": "https://m.media-amazon.com/images/I/41FDTHeLDeL._SL500_.jpg",
            "Description": "Nike founder Phil Knight recounts his raw entrepreneurial journey—from selling shoes from a trunk to building a global empire. A story of risk, passion, grit, and relentless ambition."
        },
        {
            "title": "The Power of Your Subconscious Mind",
            "image": "https://delhibookmarket.com/wp-content/uploads/2023/09/The-Power-of-Your-Subconscious-Mind.jpg",
            "Description": "Dr. Joseph Murphy explores how subconscious beliefs shape our reality. Learn how positive thinking, visualization, and belief can unlock success, health, and happiness in life and business."
        },
        {
            "title": "START WITH WHY",
            "image": "https://m.media-amazon.com/images/I/41Px2q4eSiL._SL500_.jpg",
            "Description": "Simon Sinek shows how purpose-driven leadership inspires trust, loyalty, and success. By understanding and communicating your 'why,' you can build stronger brands, movements, and lasting customer relationships."
        },
    ],
}




# --- News categories (with placeholder images) ---
news_categories = [
    {"slug": "National Politics","label": "National Politics","image": "https://images.indianexpress.com/2023/05/ch1470490.jpg"},
    {"slug": "Economy & Business","label": "Economy & Business", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmMiDdeXGeGb3DqFGV8E4xC-0E7UY5ZfTL7g&s"},
    {"slug": "Sports", "label": "Sports","image": "https://superblog.supercdn.cloud/site_cuid_clr6oh1no0006rmr89yhkxgu8/images/image-41-3-1712752581555-compressed.png"},
    {"slug": "Technology & Startups","label": "Technology & Startups","image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRCZWh8B44IJwhKhbh3_H1t5YCFBbvWL-a0lw&s"},
    {"slug": "Entertainment",    "label": "Entertainment",  "image": "https://5.imimg.com/data5/ML/PH/MY-36832343/entertainment-event-managment-500x500.jpg"},
    {"slug": "Geo-Politics","label": "Geo-Politics", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRLQwsCCJrBBweW3ozHzdxsJAQHG9OBImABYw&s"},
]

# --- Pages ---
def render_home():
    st.title("📚 Welcome to the Media App")
    st.subheader("Choose your content")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("News", "?page=news", icon="📰")
    with col2:
        st.link_button("Audiobooks", "?page=audiobooks", icon="🎧")

def render_news():
    st.sidebar.link_button("⬅ Back to Home", "?page=home")
    st.sidebar.markdown("## More in News")
    st.sidebar.button("Expert Advice", on_click=lambda: st.experimental_set_query_params(page="expert_advice"))
    st.sidebar.button("Daily News Update", on_click=lambda: st.experimental_set_query_params(page="daily_update"))

    # centered title without icon
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
          <h2 style="margin: 0; color: white;">News Categories</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for i in range(0, len(news_categories), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(news_categories):
                cat = news_categories[idx]
                card_html = f"""
                <a href="?page=category_{cat['slug']}" style="text-decoration:none;">
                  <div style="
                    border:1px solid #444;
                    border-radius:10px;
                    overflow:hidden;
                    box-shadow:2px 2px 8px rgba(0,0,0,0.5);
                    margin-bottom:20px;
                    background:#1e1e1e;
                    display:flex;
                    flex-direction:column;
                  ">
                    <img src="{cat['image']}"
                         style="
                           width:100%;
                           height:280px;           /* match your book cover height */
                           object-fit:cover;
                           display:block;
                         ">
                    <div style="
                           padding:10px;
                           color:white;
                           text-align:center;
                           flex-grow:1;
                           display:flex;
                           align-items:flex-end;
                           justify-content:center;
                         ">
                      <h4 style="margin:0; font-size:16px;">{cat['label']}</h4>
                    </div>
                  </div>
                </a>
                """
                with cols[j]:
                    st.markdown(card_html, unsafe_allow_html=True)


#####
def render_category_page(slug):
    cat = next((c for c in news_categories if c["slug"] == slug), None)
    if not cat:
        st.error("Category not found.")
        return

    st.sidebar.link_button("⬅ Back to News", "?page=news")

    # Centered title without icon
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 15px;">
          <h2 style="margin: 0; color: white;">{cat['label']}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(f"Display latest **{cat['label']}** articles here.")


def render_expert_advice():
    st.sidebar.link_button("⬅ Back to News", "?page=news")
    st.header("💡 Expert Advice")
    st.write("Curated expert tips or interviews.")

def render_daily_update():
    st.sidebar.link_button("⬅ Back to News", "?page=news")
    st.header("📅 Daily News Update")
    st.write("Daily digest of top headlines.")



def render_audiobooks():
    st.sidebar.link_button("⬅ Back to Home", "?page=home")
    genre = st.sidebar.radio("Choose Genre", list(genres.keys()))
    st.header(f"🎧 Audiobooks - {genre}")

    for i in range(0, len(genres[genre]), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(genres[genre]):
                book = genres[genre][i + j]
                slug = book['title'].replace(" ", "_")
                book_url = f"?page=book_{slug}"

                # card_html = f"""
                # <a href="{book_url}" style="text-decoration: none;">
                #     <div style="border: 1px solid #ddd; border-radius: 10px; overflow: hidden; box-shadow: 2px 2px 10px #eee; margin-bottom: 20px;">
                #         <img src="{book['image']}" style="width: 100%; height: 320px; object-fit: cover; display: block;">
                #         <div style="padding: 10px; color: black;">
                #             <h4 style="margin: 0; font-size: 16px; text-align: center;">{book['title']}</h4>
                #             <p style="font-size: 13px; color: #555;">{book.get('Description', '')}</p>
                #         </div>
                #     </div>
                # </a>
                # """

                card_html = f"""
                <a href="{book_url}" style="text-decoration: none;">
                    <div style="border: 1px solid #ddd; border-radius: 10px; overflow: hidden; box-shadow: 2px 2px 10px #eee; margin-bottom: 20px;">
                        <img src="{book['image']}" style="width: 100%; height: 320px; object-fit: cover; display: block;">
                    </div>
                </a>
                """

                with cols[j]:
                    st.markdown(card_html, unsafe_allow_html=True)

            



# def render_book_page(title_slug):
#     st.sidebar.link_button("⬅ Back to Genres", "?page=audiobooks")

#     for genre_books in genres.values():
#         for book in genre_books:
#             if book['title'].replace(" ", "_") == title_slug:
#                 st.markdown(f"<h2 style='text-align: center;'>{book['title']}</h2>", unsafe_allow_html=True)
                
#                 # ⬅️ CENTER IMAGE
#                 col1, col2, col3 = st.columns([1, 2, 1])
#                 with col2:
#                     st.image(book['image'], use_container_width=True)
#                     # st.image(book['image'], use_column_width=True)

#                 # 📖 Show Description
#                 st.markdown("#### 📖 Book details")
#                 description = book.get("Description", "No description available.")
#                 st.write(description)

#                 return

#     st.error("Book not found.")

audio_files = {
    "Deep Work": "Deep Work.wav",
    "The Republic": "The-Republic-Plato.wav",
    "Brief Answers to the Big Questions": "stephen_hawking_a_brief_history_of_time.wav",
    "Sample Audio": "aud.wav",
}


def render_book_page(title_slug):
    st.sidebar.link_button("⬅ Back to Genres", "?page=audiobooks")

    for genre_books in genres.values():
        for book in genre_books:
            if book['title'].replace(" ", "_") == title_slug:
                st.markdown(f"<h2 style='text-align: center;'>{book['title']}</h2>", unsafe_allow_html=True)

                # Center image
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(book['image'], use_container_width=True)

                # Description
                st.markdown("#### 📖 Book details")
                description = book.get("Description", "No description available.")
                st.write(description)

                # Audio section
                st.markdown("---")
                st.subheader("🎧 Listen to Audio")

                # Look up audio filename from mapping
                audio_filename = audio_files.get(book['title'])

                if audio_filename:
                    audio_path = f"audio/{audio_filename}"
                    try:
                        with open(audio_path, "rb") as audio_file:
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format="audio/wav")
                    except FileNotFoundError:
                        st.warning("Audio file found in mapping but not found in folder.")
                else:
                    st.info("No audio available for this book.")

                return

    st.error("Book not found.")






# # --- Routing Logic ---
# if page == "home":
#     render_home()
# elif page == "news":
#     render_news()
# elif page == "audiobooks":
#     render_audiobooks()
# elif page.startswith("book_"):
#     render_book_page(page[5:])
# else:
#     st.error("Page not found.")


# --- Routing Logic ---
if page == "home":
    render_home()
elif page == "news":
    render_news()
elif page.startswith("category_"):
    render_category_page(page.split("_", 1)[1])
elif page == "expert_advice":
    render_expert_advice()
elif page == "daily_update":
    render_daily_update()
elif page == "audiobooks":
    render_audiobooks()
elif page.startswith("book_"):
    render_book_page(page[5:])
else:
    st.error("Page not found.")








