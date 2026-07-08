const searchBar = document.getElementById("search-input");
const dropDownResults = document.getElementById("drop-down-results");
const sideBarExit = document.querySelector(".side-exit");
const sideBar = document.querySelector(".side-bar");
const openSideBtn = document.querySelector(".side-btn");

function closeSideBar() {
  Array.from(sideBar.children).forEach((child) => {
    child.style.display = "none";
  });
  sideBar.style.width = "0%";
}
let timer;
function openSideBar() {
  sideBar.style.width = "20%";

  timer = setTimeout(() => {
    Array.from(sideBar.children).forEach((child) => {
      child.style.display = "block";
    });
    return clearTimeout(timer);
  }, 900);
}

openSideBtn.addEventListener("click", openSideBar);
sideBarExit.addEventListener("click", closeSideBar);

window.onclick = function (event) {
  if (!(event.target === searchBar) && !(event.target === openSideBtn)) {
    closeSideBar();
    this.clearTimeout(timer);
  }
};

function searchQuery() {
  const query = searchBar.value.trim();

  if (query.length === 0) {
    dropDownResults.innerHTML = '<div id=drop-down-results"></div>';
    return;
  }

  fetch(`../../api/search/?q=${encodeURIComponent(query)}`)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      if (data.item.length === 0) {
        const pageResponse = '<h3 class="not-found" > No items found </h3>';
        dropDownResults.innerHTML = pageResponse;

        return;
      }
      dropDownResults.innerHTML = "";
      data.item.forEach((results) => {
        const pageResponse = `
            <a title = "Go to item" class="drop-down-link" href="/users/?q=${encodeURIComponent(results.lender.link)}#${results.items.id}">
                <div class="drop-down-rs">
                    <div class="search-rs-header">
                        <p class="search-rs-itemname">${results.items.name}</p>
                        <p class="search-rs-lendername">${results.lender.name}</p>
                    </div>
                    <div class="search-rs-itemrs">
                        <h4 class="item-desc-name">Item description</h4>
                        <p class="search-rs-item-desc">${results.items.desc}</p>
                    </div>
                    <img class="search-item-image" src="${results.items.urlImage}" alt="NO IMAGE" />
                </div> 
            </a>     
        `;

        dropDownResults.insertAdjacentHTML("beforeend", pageResponse);
      });
    });
}
let timeout;
searchBar.addEventListener("input", () => {
  clearTimeout(timeout);

  timeout = setTimeout(() => {
    searchQuery();
  }, 800);

  if (searchBar.value.length === 0) {
    clearTimeout(timeout);
    searchQuery();
  }
  return;
});
