On PC/Laptop should be installed Docker/Docker compose, 
* docker
* docker-compose
* git
* make

## Instuction
* *git clone https://github.com/v-kolesov/markets-demo.git*
* *cd markets-demo*
* *make upb*

## Run Test
* *docker  exec -it   market_demo  pytest*

## Web Interface
*firefox http://localhost:5000/*

Click on **users** (it is collapcable block). Then click on block **POST /users/login**. In this blog press **Try It Out** button, than **Execute** button. In a field **Response body** copy value of token. On a top of page press the **Autorize** green button. Paste value of token and post it with **"ok"**. Now click on **GET /users/auth/logs** and **Try It Out** button here. Change some **Parameters** and press **Execute**


PS. Databases filled with users from https://github.com/v-kolesov/markets-demo/blob/master/api/default_users.py. Fill free to pick any of them for test perpose.
