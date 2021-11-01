import streamlit as st
from db import database
import pandas as pd
from hash import hash
from algorithms import equal_weight_SnP_500, momentum_strategy, value_strategy
import stock

def main():

    st.title("Algo Trading")

    menu = ["Home","Login","SignUp"]
    choice = st.sidebar.selectbox("Menu",menu)
    db = database()
    hashing = hash()

    if choice == "Home":
        st.subheader("Home")
        stock.main()

    elif choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox("Login"):
            # if password == '12345':
            db.create_usertable()
            hashed_pswd = hashing.make_hashes(password)

            result = db.login_user(username, hashing.check_hashes(password,hashed_pswd))
            if result:

                st.success("Logged In as {}".format(username))

                task = st.selectbox("Choose your desired investment strategy ",["...", "Equal weight protfolio", "Momentum strategy", "Value investing"])
                if task == "...":
                    pass
                elif task == "Equal weight protfolio":
                    equal_weight_SnP_500.main()

                elif task == "Momentum strategy":
                    momentum_strategy.main()

                elif task == "Value investing":
                    value_strategy.main()
                    
            else:
                st.warning("Incorrect Username/Password")





    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')

        if st.button("Signup"):
            db.create_usertable()
            db.add_userdata(new_user, hashing.make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

if __name__ == '__main__':
    main()