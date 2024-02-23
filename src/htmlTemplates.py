css = '''<style>
/* styles.css */

body {
    font-family: Arial, sans-serif;

.container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 20px;
    overflow-y: auto;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 70px; /* Espace pour le champ de saisie utilisateur */
}

.chat-message {
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
}

.user .avatar img,
.bot .avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 10px;
}

.message {
    padding: 10px 15px;
    border-radius: 10px;
    max-width: 70%;
    word-wrap: break-word;
    color: black;
}

.user .message {
    background-color: #DCF8C6;
}

.bot .message {
    background-color: #E5E5EA;
}

.input-container {
    padding-top: 20px;
    padding-bottom: 20px;
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: white;
    z-index: 1;
    border-top: 1px solid #ccc;
}

.user-question {
    position: fixed;
    bottom: 0;
    width: 100%;
    padding: 10px;
    background-color: white;
    border-top: 1px solid #ccc;
    z-index: 2;
    overflow-y: hidden;
}

/* Styles pour le bouton */
.stButton>button {
    background-color: #186F65; /* Vert */
    border: none;
    color: white;
    padding: 10px 30px;
    text-align: center;
    text-decoration: None;
    display: inline-block;
    font-size: 18px;
    margin: 4px 2px;
    transition-duration: 0.4s;
    cursor: pointer;
    border-radius: 12px;
}

# .stButton>button:hover {
#     background-color: #45a049; /* Vert foncé */
# }

''' 

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://digitar.be/wp-content/uploads/2017/11/logo-white-transp.png">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
