// Hiển thị hình ảnh khi người dùng tải lên
function previewImage(event) {
  const imagePreview = document.getElementById('imagePreview');
  const imageInput = event.target.files[0];
  
  if (imageInput) {
      const reader = new FileReader();
      
      reader.onload = function(e) {
          imagePreview.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image">`;
      };
      
      reader.readAsDataURL(imageInput);
  } else {
      imagePreview.innerHTML = ""; // Xóa hình ảnh nếu không có ảnh được chọn
  }
}

// Chức năng chẩn đoán
function diagnose() {
  const imageInput = document.getElementById('imageUpload');
  const modalResult = document.getElementById('modalResult');
  
  if (imageInput.files.length === 0) {
      modalResult.innerHTML = "Please upload an image first.";
      showModal();
      return;
  }

  // Giả lập quá trình chẩn đoán
  modalResult.innerHTML = "Diagnosing...";
  showModal();
  
  // Giả sử sau vài giây có kết quả
  setTimeout(() => {
      modalResult.innerHTML = "Diagnosis Complete: High risk of stroke detected.";
  }, 2000);
}

// Mở modal
function showModal() {
  const modal = document.getElementById('resultModal');
  modal.style.display = "flex";
}

// Đóng modal
function closeModal() {
  const modal = document.getElementById('resultModal');
  modal.style.display = "none";
}

// Đóng modal khi nhấp ngoài vùng modal-content
window.onclick = function(event) {
  const modal = document.getElementById('resultModal');
  if (event.target === modal) {
      modal.style.display = "none";
  }
}

// Dropdown menu cho Admin
var dropdown = document.getElementById("avatarDropdown");
var avatar = document.getElementById("avatar");

avatar.onclick = function(event) {
    event.stopPropagation(); 
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

window.onclick = function(event) {
    if (!event.target.matches('.admin-avatar') && dropdown.style.display === "block") {
        dropdown.style.display = "none";
    }
}

// Cài đặt modal cho nhiều modal khác nhau
document.addEventListener('DOMContentLoaded', function () {
  function setupModal(modalId, openBtnId, closeBtnId) {
    const modal = document.getElementById(modalId);
    const openModalBtn = document.getElementById(openBtnId);
    const closeModalBtn = document.getElementById(closeBtnId);

    if (!modal || !openModalBtn || !closeModalBtn) {
      console.warn(`Modal setup failed: Missing elements for ${modalId}`);
      return;
    }

    // Mở modal khi nhấn nút mở
    openModalBtn.addEventListener('click', () => {
      modal.style.display = 'flex';
    });

    // Đóng modal khi nhấn nút đóng
    closeModalBtn.addEventListener('click', () => {
      modal.style.display = 'none';
    });

    // Đóng modal khi nhấn bên ngoài nội dung modal
    window.addEventListener('click', (event) => {
      if (event.target === modal) {
        modal.style.display = 'none';
      }
    });
  }

  // Gọi hàm setupModal cho các modal khác nhau
  setupModal('infoModal', 'openModal', 'closeModal');
  setupModal('infoModal-Systemsetup', 'openModal-2', 'closeModal-2');
  setupModal('infoModal-ImageStory', 'openModal-3', 'closeModal-3');
  setupModal('infoModal-StorySearch', 'openModal-4', 'closeModal-4');
  setupModal('infoModal-Storyresult', 'openModal-5', 'closeModal-5');
  setupModal('infoModal-DatasetStoke', 'openModal-6', 'closeModal-6');
});

// Xử lý form loan prediction
document.getElementById('loanPredictionForm').addEventListener('submit', function(event) {
  event.preventDefault();

  // Thu thập dữ liệu form
  const formData = new FormData(this);
  const data = {};
  formData.forEach((value, key) => {
      data[key] = value;
  });

  // Gửi dữ liệu form đến server hoặc xử lý dự đoán (thực hiện thông qua API)
  console.log(data);  // Hiện tại chỉ log dữ liệu ra console.

  // Hiển thị modal kết quả (có thể tùy chỉnh thêm)
  document.getElementById('resultModal').style.display = 'flex';
  document.getElementById('modalResult').innerText = 'Prediction results will appear here.';
});


// Hiển thị modal kết quả
function showModal() {
  const modal = document.getElementById('resultModal');
  modal.style.display = "flex";
}

// Đóng modal
function closeModal() {
  const modal = document.getElementById('resultModal');
  modal.style.display = "none";
}




