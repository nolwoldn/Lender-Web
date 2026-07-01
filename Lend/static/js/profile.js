const lendItemBtn = document.querySelector(".Lend-item");
const closeLendBtn = document.querySelector(".close-lend-form");
const lendForm = document.querySelector(".lending");

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
      console.error(`Error : ${myResponse.e}`);
    }
  } catch (error) {
    console.log(error);
  }
}

lendItemSubmit.addEventListener("click", (event) => {
  const itemName = document.querySelector("#lending-item-name");
  const itemDesc = document.querySelector("#lending-item-desc");

  closeForm(lendForm);

  const fixedData = {
    itemName: itemName.value.trim(),
    itemDesc: itemDesc.value.trim(),
  };

  sendToServer("lendingItem", fixedData);
});

if (returnBrrwdItem.length > 0) {
  returnBrrwdItem.forEach((reElement) => {
    reElement.addEventListener("click", (event) => {
      const brrwdItem = event.currentTarget;
      const brrwdItemId = brrwdItem.dataset.usrBorrowedItem;
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

      sendToServer("affectBorrowReq", fixedData);
    });
  });
}

if (editSubmitionClass.length > 0) {
  editSubmitionClass.forEach((editSubmitBtn) => {
    editSubmitBtn.addEventListener("click", (event) => {
      const subBtnDataSet = event.currentTarget.dataset;
      const itmId = subBtnDataSet.itmCardId;
      const itmNameInp = document.querySelector(
        `#${subBtnDataSet.nameInputId}`,
      );
      const itmDescInp = document.querySelector(
        `#${subBtnDataSet.descInputId}`,
      );
      const editingForm = document.querySelector(`#itm-edit-${itmId}`);
      editingForm.style.display = "none";
      const fixedData = {
        itm_Id: itmId,
        itm_new_name: itmNameInp.value,
        itm_new_desc: itmDescInp.value,
      };

      sendToServer("editItm", fixedData);
    });
  });
}

if (deleteLendedItemClass.length > 0) {
  deleteLendedItemClass.forEach((deleteItemBtn) => {
    deleteItemBtn.addEventListener("click", (event) => {
      const btnDataSet = event.currentTarget.dataset;
      const itmId = btnDataSet.itmId;

      sendToServer("delete_itm", itmId);
    });
  });
}
