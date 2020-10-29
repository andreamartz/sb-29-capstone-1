const BASE_URL = "/api/get-videos";
const form = document.querySelector('#keyword-search-form');
const course_id = document.querySelector('#course-id').value;
const searchResults = document.querySelector("#search-results");
let keywordErr = document.querySelector("#keyword-err");

/** processKeywordSearchForm: get data from form and make AJAX call to Flask API */
async function processKeywordSearchForm(evt) {
  evt.preventDefault();
  // get data from keyword search form
  const keyword = document.querySelector("#keyword").value;
  const formData = {keyword};
  // CHANGE: remove console.log
  console.log("keyword: ", keyword, "formData: ", formData);

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
  // searchResultsVideos.innerText = '';
  searchResults.innerText = '';
  const res_errors = res["data"]["errors"]

  if (res_errors) {
    if (res_errors["keyword"]) {
      keywordErr.innerText = res_errors["keyword"][0];
    }
  } else {
    const videos = res['data'];
    for (let video of videos) {
      const videoId = video['id'];
      const title = video['title'];
      const channelId = video['channelId'];
      const channelTitle = video['channelTitle'];
      const description = video['description'];
      const thumbUrl = video["thumb_url_high"];
      // CHANGE: uncomment this when app.py will start rendering videos, not thumbnails
      // const iframe = video['iframe'];

      const article = document.createElement("article");
      article.setAttribute("data-id", `${videoId}`);
      article.setAttribute("class", "row");
      // CHANGE: when ready to display videos instead of thumbnails, first column should show ${iframe} instead of ${thumbUrl}
      article.innerHTML = 
      `<div class="col-5">
        <img src="${thumbUrl}">
      </div>
      <div class="col-5">
        <p>Title: ${title}</p>
        <p>Description: ${description}</p>
        <form action="../../courses/${course_id}/add-video/${videoId}" method="POST">
          <input type="hidden" id="v-id" name="v-id" value="${videoId}">
          <input type="hidden" id="v-title" name="v-title" value="${title}">
          <input type="hidden" id="v-description" name="v-description" value="${description}">
          <input type="hidden" id="v-channelId" name="v-channelId" value="${channelId}">
          <input type="hidden" id="v-channelTitle" name="v-channelTitle" value="${channelTitle}">
          <input type="hidden" id="v-thumbUrl" name="v-thumbUrl" value="${thumbUrl}">
          <button type="submit" class="btn btn-primary">Add to course</button>
        </form>
      </div>`;
      // CHANGE: add the following back to the article's innerHTML above when app.py will start rendering videos, not thumbnails
      // <input type="hidden" id="v-iframe" name="v-iframe" value="${iframe}">

      searchResults.append(
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

