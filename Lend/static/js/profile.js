const lendItemBtn = document.querySelector(".Lend-item");
const closeLendBtn = document.querySelector(".close-lend-form");
const lendForm = document.querySelector(".lending");
const lendingItemImage = document.querySelector(".item-image");
const lendingImagePrev = document.querySelector("#image-preview");
const editingImageInputClass = document.querySelectorAll(".editing-prev");
const errorExplainer = document.querySelector(".error-explanation");

const lendItemSubmit = document.querySelector(".submit-button");
const requestAnsClass = document.querySelectorAll(".request-ans");
const editSubmitionClass = document.querySelectorAll(".edit-submit");
const deleteLendedItemClass = document.querySelectorAll(".delete");
const returnBrrwdItem = document.querySelectorAll(".brrw-itm-re");

function openForm(el) {
  el.style.display = "block";
}
function closeForm(el) {
  el.style.display = "none";
}

lendItemBtn.addEventListener("click", () => openForm(lendForm));
closeLendBtn.addEventListener("click", () => closeForm(lendForm));

let displayTimer;

function changeErrorExplainer(message) {
  errorExplainer.innerHTML = message;
  errorExplainer.style.display = "block";
  clearTimeout(displayTimer);
  displayTimer = setTimeout(() => {
    errorExplainer.innerHTML = "";
    errorExplainer.style.display = "none";
  }, 1200);
}

window.onclick = function (event) {
  if (
    !(event.target === lendForm || lendForm.contains(event.target)) &&
    !(event.target === lendItemBtn)
  ) {
    closeForm(lendForm);
  }
};

async function sendToServer(action, data) {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const url = window.location.href;

  const payload = {
    action: action,
    data: data,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(payload),
    });

    const myResponse = response.json();

    if (myResponse.worked) {
      window.location.href = window.location.href;
    } else {
    }
  } catch (error) {
    console.log(error);
  }
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
} //chose the stupidest way for no reason but for the lols

lendItemSubmit.addEventListener("click", async (event) => {
  const itemName = document.querySelector("#lending-item-name");
  const itemDesc = document.querySelector("#lending-item-desc");
  const itemImageFile = lendingItemImage.files[0];

  closeForm(lendForm);

  let base64Image = null;
  if (itemImageFile) {
    base64Image = await fileToBase64(itemImageFile);
  }

  const fixedData = {
    itemName: itemName.value.trim(),
    itemDesc: itemDesc.value.trim(),
    itemImage: base64Image,
  };
  changeErrorExplainer("Item lended, please reload the page to see effects");
  sendToServer("lendingItem", fixedData);
});

if (returnBrrwdItem.length > 0) {
  returnBrrwdItem.forEach((reElement) => {
    reElement.addEventListener("click", (event) => {
      const brrwdItem = event.currentTarget;
      const brrwdItemId = brrwdItem.dataset.usrBorrowedItem;
      changeErrorExplainer("Item returned, reload to see effects");
      sendToServer("returnItem", brrwdItemId);
    });
  });
}

if (requestAnsClass.length > 0) {
  requestAnsClass.forEach((requestAns) => {
    requestAns.addEventListener("click", (event) => {
      const crrelement = event.currentTarget;
      const borrowReqId = crrelement.dataset.brrReqD;
      const acceptance = crrelement.dataset.brrqType;
      const fixedData = {
        borrowId: borrowReqId,
        isAccepted: acceptance,
      };
      changeErrorExplainer(
        "Borrowe request decsion made, please reload to see effects",
      );
      sendToServer("affectBorrowReq", fixedData);
    });
  });
}

if (editSubmitionClass.length > 0) {
  editSubmitionClass.forEach((editSubmitBtn) => {
    editSubmitBtn.addEventListener("click", async (event) => {
      const subBtnDataSet = event.currentTarget.dataset;
      const itmId = subBtnDataSet.itmCardId;

      const itmNameInp = document.getElementById(subBtnDataSet.nameInputId);
      const itmDescInp = document.getElementById(subBtnDataSet.descInputId);
      const itmImgInp = document.querySelector(`.${subBtnDataSet.imgInputId}`);
      const itmImgFile = itmImgInp.files[0];

      const editingForm = document.querySelector(`#itm-edit-${itmId}`);
      editingForm.style.display = "none";
      let itmImgString;

      if (itmImgFile) {
        itmImgString = await fileToBase64(itmImgFile);
      } else {
        itmImgString = null;
      }

      const fixedData = {
        itm_Id: itmId,
        itm_new_name: itmNameInp.value,
        itm_new_desc: itmDescInp.value,
        itm_new_img: itmImgString,
      };
      changeErrorExplainer("Item edited reload to see effects");
      sendToServer("editItm", fixedData);
    });
  });
}

if (deleteLendedItemClass.length > 0) {
  deleteLendedItemClass.forEach((deleteItemBtn) => {
    deleteItemBtn.addEventListener("click", (event) => {
      const btnDataSet = event.currentTarget.dataset;
      const itmId = btnDataSet.itmId;

      changeErrorExplainer("Item deleted, please reload to see effects");
      sendToServer("delete_itm", itmId);
    });
  });
}

lendingItemImage.addEventListener("change", function () {
  const crrImageFile = this.files[0];

  if (crrImageFile) {
    const objectUrl = URL.createObjectURL(crrImageFile);

    lendingImagePrev.src = objectUrl;
    lendingImagePrev.style.display = "block";
  } else {
    lendingImagePrev.src = "";
    lendingImagePrev.style.display = "none";
  }
});

if (editingImageInputClass.length > 0) {
  editingImageInputClass.forEach((editingImageInp) => {
    editingImageInp.addEventListener("change", function (event) {
      const editingImageInpDataSet = this.dataset;
      const editingImgPrev = document.getElementById(
        editingImageInpDataSet.swapImgId,
      );
      const crrItemFile = this.files[0];

      if (crrItemFile) {
        const crrObjectUrl = URL.createObjectURL(crrItemFile);

        editingImgPrev.src = crrObjectUrl;
      } else {
      }
    });
  });
}
