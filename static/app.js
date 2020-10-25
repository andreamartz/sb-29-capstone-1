/** processKeywordSearchForm: get data from form and make AJAX call to Flask API */

const BASE_URL = "/api/get-videos";
const form = document.querySelector('#keyword-search-form');
const keywordSearchResults = document.querySelector("#keyword-search-results");
let keywordErr = document.querySelector("#keyword-err");

async function processKeywordSearchForm(evt) {
  evt.preventDefault();

  // get data from keyword search form
  const keyword = document.querySelector("#keyword").value;
  const formData = {keyword};

  // make AJAX call to our Flask API
  const res = await axios({
    method: 'post',
    url: `${BASE_URL}`,
    responseType: 'json',
    data: formData,
  });
  console.log("res: ", res);
  return res;
}

/** handleResponse: deal with response from our get-videos app */
function handleResponse(res) {
  keywordErr.innerText = '';
  const res_errors = res["data"]["errors"]

  if (res_errors) {
    if (res_errors["keyword"]) {
      keywordErr.innerText = res_errors["keyword"][0];
    }
  } else {
    let videos = res['data'];
    for (let video of videos) {
      let thumb_url = video["thumb_url_high"];
      const article = document.createElement("article");
      article.setAttribute("data-id", `${video['id']}`);
      article.innerHTML = 
      `<img src="${thumb_url}" alt="thumbnail of video: ${video['title']}">
      <div>
        <p>Title: ${video['title']}</p>
        <p>Description: ${video['description']}</p>
      </div>`
      keywordSearchResults.append(
        article
      );
    }
    form.reset();
  }
}

form.addEventListener("submit", async function(evt) {
  res = await processKeywordSearchForm(evt); // response from Flask backend API

  handleResponse(res);
})

