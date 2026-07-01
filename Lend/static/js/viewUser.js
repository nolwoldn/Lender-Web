const sendLinkClass = document.querySelectorAll(".itm-card");
const errorExplainer = document.querySelector(".error-explanation");

async function sendBorrowReq(data) {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const url = "../../api/borrow/";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(data),
    });

    const fixedRes = await response.json();

    switch (fixedRes.what) {
      case "nothing":
        errorExplainer.innerHTML = "Request has been sent";
        errorExplainer.style.display = "block";
        break;
      default:
        errorExplainer.innerHTML = fixedRes.what;
        errorExplainer.style.display = "block"
        break;
    }
  } catch (error) {
    console.log(error);
  }
}

if (sendLinkClass.length > 0) {
  sendLinkClass.forEach((link) => {
    link.addEventListener("click", (event) => {
      const linkDataSet = event.currentTarget.dataset;
      const brrwingFromUsrId = linkDataSet.borrowingFromUsrId;
      const brrwingItmId = linkDataSet.borrowingItmId;
      const fixedData = {
        borrowing_from_id: brrwingFromUsrId,
        borrowing_itm_id: brrwingItmId,
      };

      sendBorrowReq(fixedData);
    });
  });
}
