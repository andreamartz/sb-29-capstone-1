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
      const ytVideoId = video['ytVideoId'];
      const title = video['title'];
      const channelId = video['channelId'];
      const channelTitle = video['channelTitle'];
      const description = video['description'];
      const thumbUrl = video["thumb_url_medium"];

      const div = document.createElement("div");
      div.setAttribute("data-id", `${ytVideoId}`);
      div.setAttribute("class", "card mb-3");
      div.innerHTML = 
      `<div class="row no-gutters justify-content-center">
        <div class="col-8 col-md-4 image-container">
          <img src="${thumbUrl}" class="course-img">
        </div>
        <div class="col-8 col-md-8">
          <div class="card-body">
            <h5 class="card-title">${title}</h5>
            <p class="card-subtitle mb-2">Created by: ${channelTitle}</p>
            <p class="card-text">${description}</p>
            <form action="../../../courses/${course_id}/videos/${ytVideoId}/add" method="POST">
              <input type="hidden" id="v-yt-id" name="v-yt-id" value="${ytVideoId}">
              <input type="hidden" id="v-title" name="v-title" value="${title}">
              <input type="hidden" id="v-description" name="v-description" value="${description}">
              <input type="hidden" id="v-channelId" name="v-channelId" value="${channelId}">
              <input type="hidden" id="v-channelTitle" name="v-channelTitle" value="${channelTitle}">
              <input type="hidden" id="v-thumb_url" name="v-thumb-url" value="${thumbUrl}">
              <button type="submit" class="btn btn-primary">Add to course</button>
            </form>
          </div>
        </div>
      </div>`;
      searchResults.append(
        div
      );
    }
    form.reset();
  }
}

form.addEventListener("submit", async function(evt) {
  res = await processKeywordSearchForm(evt); // response from Flask backend API

  handleResponse(res);
})

