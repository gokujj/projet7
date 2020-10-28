const chatboxForm = document.querySelector("#chatbox-form");

/**
 * Sends a form to a remote server with the HTTP POST method
 * for its asynchronous processing.
 */
function postForm(url, form) {
    const formData = new FormData(form);

    // Envoi de la requête HTTP
    response = fetch(url, {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .catch(error => console.log(error));

    return response;
}

/**
 * Creates the HTML element containing the user's question
 */
function createUserQuestion(parent, data) {
    const chatboxMessage = document.createElement("div");
    chatboxMessage.classList.add("chatbox__message");

    const messageAvatar = document.createElement("img");
    messageAvatar.classList.add("message__avatar");
    messageAvatar.src = staticImageFolder + '/user.jpg';
    messageAvatar.alt = "user avatar";

    const messageContent = document.createElement("div");
    messageContent.classList.add("message__content");
    messageContent.appendChild(document.createTextNode(data.question));

    chatboxMessage.appendChild(messageAvatar);
    chatboxMessage.appendChild(messageContent);
    parent.appendChild(chatboxMessage);

    return chatboxMessage;
}

/**
 * Create the HTML element containing Grandpy's response
 */
function createGrandpyAnswer(parent, data) {
    const chatboxAnswer = document.createElement("div");
    chatboxAnswer.classList.add("chatbox__answer");

    createGrandpyAnswerAvatar(chatboxAnswer, data);
    createGrandpyAnswerContent(chatboxAnswer, data);
    createGrandpyAnswerMap(chatboxAnswer, data);
    createGrandpyAnswerIntro(chatboxAnswer, data);
    createGrandpyAnswerArticle(chatboxAnswer, data);
    createGrandpyAnswerLink(chatboxAnswer, data);

    parent.appendChild(chatboxAnswer);
    return chatboxAnswer;
}

/**
 * Build the HTML element containing Grandpy's avatar
 */
function createGrandpyAnswerAvatar(parent, data) {
    const answerAvatar = document.createElement("img");
    answerAvatar.classList.add("answer__avatar");
    answerAvatar.src = staticImageFolder + "/grandpy.jpg";
    answerAvatar.alt = "Grandpy avatar";

    parent.appendChild(answerAvatar);
}

/**
 * Builds the HTML element containing Grandpy's random response with the address.
 */
function createGrandpyAnswerContent(parent, data) {
    const content = data.answer + data.address;

    const answerContent = document.createElement("p");
    answerContent.classList.add("answer__content");
    answerContent.appendChild(document.createTextNode(content));

    parent.appendChild(answerContent);
}

/**
 * Create an interactive map from latitutde and longitude
 * contained in data. The HTML element containing the map is added in
 * parent.
 */
function createGrandpyAnswerMap(parent, data) {
    const answerMap = document.createElement("div");
    answerMap.classList.add("answer__map");

    const location = { lat: data.latitude, lng: data.longitude };

    // Call to the Google Maps javascript API
    const map = new google.maps.Map(answerMap, {
      zoom: 10,
      center: location,
    });
    new google.maps.Marker({
      position: location,
      map,
      title: data.answer,
    });

    // Adding the map to the parent element
    parent.appendChild(answerMap);
}

/**
 * Creates the HTML element containing the introduction of the article by Grandpy.
 *     <p class = "answer__intro"> Here is some information about your request: </p>
 */
function createGrandpyAnswerIntro(parent, data) {
    const answerIntro = document.createElement("p");
    answerIntro.classList.add("answer__intro");
    answerIntro.appendChild(document.createTextNode(data.intro));

    parent.appendChild(answerIntro);
}

/**
 * Creates the HTML element containing the wikipedia article.
 */
function createGrandpyAnswerArticle(parent, data) {
    const answerArticle = document.createElement("p");
    answerArticle.classList.add("answer__article");
    answerArticle.appendChild(document.createTextNode(data.summary));

    parent.appendChild(answerArticle);
}

// Creates the HTML element containing the link to the wikipedia article.
function createGrandpyAnswerLink(parent, data) {
    const answerLink = document.createElement("a");
    answerLink.classList.add("answer__link");
    answerLink.textContent = "En savoir plus";
    answerLink.href = data.url;

    parent.appendChild(answerLink);
}

/**
 * Build a negative response from Grandpy and add it to the page (DOM)
 */
function handleGrandpyNegativeAnswer(data) {
    const chatbox = document.querySelector("#chatbox");
    const chatboxMessage = createUserQuestion(chatbox, data);
    const chatboxAnswer = createGrandpyNegativeAnswer(chatbox, data);

    chatboxMessage.scrollIntoView();
}

/**
 *  Construct the HTML element for a negative response from Grandpy.
 */
function createGrandpyNegativeAnswer(parent, data) {
    const chatboxAnswer = document.createElement("div");
    chatboxAnswer.classList.add("chatbox__answer");

    createGrandpyAnswerAvatar(chatboxAnswer, data);

    const answerContent = document.createElement("p");
    answerContent.classList.add(
        "chatbox__answer",
        "chatbox__answer--negative"
    );
    answerContent.appendChild(document.createTextNode(data.answer));

    parent.appendChild(answerContent);

    return chatboxAnswer;
}

/**
 * Build a positive response from Grandpy and add it to the page (DOM)
 */
function handleGrandpyPositiveAnswer(data) {
    const chatbox = document.querySelector("#chatbox");
    const chatboxMessage = createUserQuestion(chatbox, data);
    const chatboxAnswer = createGrandpyAnswer(chatbox, data);

    chatboxMessage.scrollIntoView();
}

/**
 * Change the state of the mouse to display an animation showing the wait.
 */
function toggleCursorToWait() {
    document.body.classList.toggle("waiting");

    const chatboxButton = document.querySelector(".chatbox__button");
    chatboxButton.classList.toggle("waiting");
}

/**
 * Adds an event handler to process the form submission.
 * The submission uses an HTTP request in ajax.
 */
chatboxForm.addEventListener("submit", function (event) {
    event.preventDefault();

    // We change the state of the mouse to ask the user to wait
    toggleCursorToWait();

    postForm("/question", chatboxForm)
    .then(response => {
        if (response.found) {
            handleGrandpyPositiveAnswer(response);
        } else {
            handleGrandpyNegativeAnswer(response);
        }

        // Return to default mouse
        toggleCursorToWait();
    });
});
