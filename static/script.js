/* For index.html */

// TODO: If a user clicks to create a chat, create an auth key for them
// and save it. Redirect the user to /chat/<chat_id>
function createChat() {
  const myInit = {
    method: 'POST',
    headers: {
      'Authorization' : WATCH_PARTY_API_KEY
    }
  };

  fetch('/rooms/new', myInit)
  .then(response => response.json())
  .then(data => {
    console.log(data)
    console.log(data.roomId)

    if (data.room_id) {
      window.location.href = `/rooms/${data.room_id}`;
    } else {
      console.error('Failed to create a room');
    }
  })
  .catch(error => console.error('Error:', error));
}


/* For room.html */

// TODO: Fetch the list of existing chat messages.
// POST to the API when the user posts a new message.
// Automatically poll for new messages on a regular interval.
function postMessage() {
  console.log("js postMessage() method")
  const messageInput = document.querySelector('.comment_box textarea');
  const message = messageInput.value;
  const inviteLinkElement = document.querySelector('.invite a');
  const hrefValue = inviteLinkElement.getAttribute('href');
  const roomId = hrefValue.split('/')[2];

  let queryurl = "/api/rooms/" + roomId + "/messages";
  fetch(queryurl, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'Authorization': WATCH_PARTY_API_KEY
      },
      body: JSON.stringify({ body: message, user_id: WATCH_PARTY_USER_ID })
  })
  .then(response => {
      if (response.ok) {
          document.querySelector('.comment_box textarea').value = '';
          getMessages();
      } else {
          console.error('Failed to post message');
      }
  })
  .catch(error => console.error('Error:', error));
}

function getMessages() {
  const inviteLinkElement = document.querySelector('.invite a');
  const hrefValue = inviteLinkElement.getAttribute('href');
  const roomId = hrefValue.split('/')[2];
  console.log(roomId);
  let queryurl = "/api/rooms/" + roomId + "/messages";
  console.log(queryurl);
  console.log(WATCH_PARTY_API_KEY);
  const myInit = {
    method : "GET",
    headers: {
      'Authorization': WATCH_PARTY_API_KEY
    }
  }

  fetch(queryurl, myInit)
  .then(response => response.json())
  .then(messages => {
      const messagesContainer = document.querySelector('.messages');
      messagesContainer.innerHTML = '';

      messages.forEach(message => {
          const messageElement = document.createElement('message');
          const authorElement = document.createElement('author');
          const contentElement = document.createElement('content');

          authorElement.textContent = message.name;
          contentElement.textContent = message.body;

          messageElement.appendChild(authorElement);
          messageElement.appendChild(contentElement);

          messagesContainer.appendChild(messageElement);
      });
  })
}

function editAndhide() {
  document.querySelector('.roomData .edit').classList.remove('hide');
  document.querySelector('.roomData .display').classList.add('hide'); 
  return false;
}


function updatRoomName() {
  const inviteLinkElement = document.querySelector('.invite a');
  const hrefValue = inviteLinkElement.getAttribute('href');
  const roomId = hrefValue.split('/')[2];

  const newRoomName = document.querySelector('.roomData .edit input').value;
  console.log('newRoomName', newRoomName);
  let queryurl = "/api/rooms/"+roomId;
  fetch(queryurl, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'Authorization': WATCH_PARTY_API_KEY
      },
      body: JSON.stringify({ name: newRoomName })
  })
  .then(response => {
      if (response.ok) {
          document.querySelector('.roomData .roomName').textContent = newRoomName;
          document.querySelector('.roomData .display').classList.remove('hide');
          document.querySelector('.roomData .edit').classList.add('hide');
      } else {
          console.error('Failed to update room name');
      }
  })
  .catch(error => console.error('Error:', error));
  return false;
}
function startMessagePolling() {
  setInterval(getMessages, 100);
}


function updateUsername() {
  const newUserName = document.querySelector('input[name="username"]').value;
  console.log('newUserName', newUserName);
  let queryurl = "/api/user/name";
  fetch(queryurl, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'Authorization': WATCH_PARTY_API_KEY
      },
      body: JSON.stringify({ name: newUserName })
  })
  .then(response => {
      if (response.ok) {
          alert('New Username Applied!');
      } else {
        alert('Failed to update the username.');
      }
  })
  .catch(error => console.error('Error:', error));
  return false;
}

function updatePassword() {
  const newPassword = document.querySelector('input[name="password"]').value;
  console.log('newPassword', newPassword);
  let queryurl = "/api/user/password";
  fetch(queryurl, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'Authorization': WATCH_PARTY_API_KEY
      },
      body: JSON.stringify({ password: newPassword })
  })
  .then(response => {
      if (response.ok) {
          alert('New newPassword Applied!');
      } else {
        alert('Failed to update the Password.');
      }
  })
  .catch(error => console.error('Error:', error));
  return false;
}