import streamlit as st
import pandas as pd
import random
import os

# CSV file for storing user data
CSV_FILE = "user_data.csv"

# Initialize CSV if not exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["username", "password", "wallet"])
    df.to_csv(CSV_FILE, index=False)

def load_users():
    # Read CSV file and convert columns to string types
    users = pd.read_csv(CSV_FILE)
    users["username"] = users["username"].astype(str).str.strip()  # Ensure username is a string and remove whitespace
    users["password"] = users["password"].astype(str).str.strip()  # Ensure password is a string and remove whitespace
    return users


# Save user data
def save_users(users_df):
    users_df.to_csv(CSV_FILE, index=False)

def login_page():
    st.title("Login")
    username = st.text_input("Username").strip()  # Strip whitespace
    password = st.text_input("Password", type="password").strip()

    if st.button("Login"):
        try:
            users = load_users()  # Load the user data
            if users.empty:
                st.error("No registered users found. Please register first.")
                return
            
            # Filter for matching username and password
            user = users[
                (users["username"].str.strip() == username) & 
                (users["password"].str.strip() == password)
            ]
            
            if not user.empty:
                st.session_state["username"] = username
                st.session_state["wallet"] = int(user.iloc[0]["wallet"])
                st.success(f"Welcome back, {username}!")
                st.session_state["current_page"] = "Game"
            else:
                st.error("Invalid username or password. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Registration Page
def register_page():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    initial_wallet = 50

    if st.button("Register"):
        users = load_users()
        if username in users["username"].values:
            st.error("Username already exists. Please choose another one.")
        else:
            new_user = pd.DataFrame([[username, password, initial_wallet]], columns=["username", "password", "wallet"])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("Registration successful! Please log in.")
            st.session_state["current_page"] = "Login"

# Game Page
def game_page():
    st.title(f"Welcome, {st.session_state['username']}!")
    st.write(f"### Your current wallet balance: {st.session_state['wallet']}")

    if st.session_state["wallet"] <= 0:
        st.error("Your wallet is empty! Please recharge to continue playing.")
        recharge_amount = st.number_input("Enter recharge amount:", min_value=1, step=1)
        if st.button("Recharge"):
            st.session_state["wallet"] += recharge_amount
            users = load_users()
            users.loc[users["username"] == st.session_state["username"], "wallet"] = st.session_state["wallet"]
            save_users(users)
            st.success(f"Wallet recharged! Current balance: {st.session_state['wallet']}")
            return

    # Game logic
    def play_game(choice):
        outcome = "win" if random.random() < 0.2 else "lose"
        if outcome == "win":
            st.session_state["wallet"] += 15
            st.success(f"You won! +15 points. Current wallet: {st.session_state['wallet']}")
        else:
            st.session_state["wallet"] -= 10
            st.error(f"You lost! -10 points. Current wallet: {st.session_state['wallet']}")
        # Update wallet in CSV
        users = load_users()
        users.loc[users["username"] == st.session_state["username"], "wallet"] = st.session_state["wallet"]
        save_users(users)

    questions = [
        {"question": "Choose your size preference", "options": ["Small", "Big"]},
        {"question": "Choose a color", "options": ["Red", "Blue", "Green", "Yellow"]},
        {"question": "Choose your favorite season", "options": ["Summer", "Winter", "Spring", "Autumn"]},
    ]

    for i, q in enumerate(questions, 1):
        st.subheader(f"Question {i}: {q['question']}")
        choice = st.radio(f"Choose one:", q["options"], key=f"q{i}")
        if st.button(f"Submit Question {i}", key=f"submit{i}"):
            play_game(choice)

    # Show top 5 players
    st.write("### Top 5 Players")
    users = load_users()
    top_users = users.sort_values(by="wallet", ascending=False).head(5)
    st.table(top_users[["username", "wallet"]])

    if st.button("Logout"):
        del st.session_state["username"]
        del st.session_state["wallet"]
        st.session_state["current_page"] = "Login"

# Main logic
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Login"

if st.session_state["current_page"] == "Login":
    login_page()
elif st.session_state["current_page"] == "Register":
    register_page()
elif st.session_state["current_page"] == "Game":
    game_page()
