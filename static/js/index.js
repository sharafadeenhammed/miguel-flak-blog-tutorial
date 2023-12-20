

async function translate(translateId, translatedId, target_language, language, buttonID) {
  const translateElem = document.getElementById(translateId);
  const translatedElem = document.getElementById(translatedId)
  const buttonElem = document.getElementById(buttonID)
  buttonElem.style.display = 'none'
  text = translateElem.innerText
  translatedElem.innerHTML = '<img src="static/img/loading.gif" alt="..."/>'
  const res = await fetch('http://localhost:8000/translate',
    {
      method: 'POST',
      body: JSON.stringify({
        text: text,
        target_language: target_language,
        language: language
      }),
      headers: {
        "Content-Type": 'application/json',
        "Charset": 'UTF-8',

      }
    }
    
  );

  const data = await res.json();
  translatedElem.innerHTML = `<p style="margin:5px 20px; background-color:#f3f3f3; padding:10px; display:block"> ${data.text}</p>` 
  buttonElem.style.display = 'inline'

}