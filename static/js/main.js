// Share & Reuse - Main JavaScript Interactions

document.addEventListener('DOMContentLoaded', function () {
  // 1. Auto-dismiss flash alerts after 5 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
      const bsAlert = bootstrap.Alert.getInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    });
  }, 5000);

  // 2. Urgent Food Expiry Countdown Timers
  const countdownElements = document.querySelectorAll('.expiry-countdown');
  if (countdownElements.length > 0) {
    function updateCountdowns() {
      const now = new Date().getTime();
      countdownElements.forEach(el => {
        const deadlineStr = el.getAttribute('data-deadline');
        if (!deadlineStr) return;
        
        const deadline = new Date(deadlineStr).getTime();
        const distance = deadline - now;

        if (distance < 0) {
          el.innerHTML = '<span class="text-danger fw-bold"><i class="bi bi-x-circle"></i> Expired</span>';
        } else {
          const hours = Math.floor(distance / (1000 * 60 * 60));
          const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((distance % (1000 * 60)) / 1000);
          
          let badgeClass = 'text-warning';
          if (hours < 2) badgeClass = 'text-danger fw-bold';
          else if (hours < 4) badgeClass = 'text-warning fw-semibold';

          el.innerHTML = `<span class="${badgeClass}"><i class="bi bi-clock-history"></i> ${hours}h ${minutes}m ${seconds}s left</span>`;
        }
      });
    }
    updateCountdowns();
    setInterval(updateCountdowns, 1000);
  }

  // 3. Category Toggle on Create Donation Page
  const foodRadio = document.getElementById('category-food');
  const clothesRadio = document.getElementById('category-clothes');
  const foodSection = document.getElementById('food-specific-fields');
  const clothesSection = document.getElementById('clothes-specific-fields');

  if (foodRadio && clothesRadio && foodSection && clothesSection) {
    function toggleCategories() {
      if (foodRadio.checked) {
        foodSection.style.display = 'block';
        clothesSection.style.display = 'none';
        // Enable/disable required attributes
        document.querySelectorAll('#food-specific-fields input, #food-specific-fields select').forEach(i => i.disabled = false);
        document.querySelectorAll('#clothes-specific-fields input, #clothes-specific-fields select').forEach(i => i.disabled = true);
      } else {
        foodSection.style.display = 'none';
        clothesSection.style.display = 'block';
        document.querySelectorAll('#food-specific-fields input, #food-specific-fields select').forEach(i => i.disabled = true);
        document.querySelectorAll('#clothes-specific-fields input, #clothes-specific-fields select').forEach(i => i.disabled = false);
      }
    }
    foodRadio.addEventListener('change', toggleCategories);
    clothesRadio.addEventListener('change', toggleCategories);
    toggleCategories(); // Initial check
  }

  // 4. Quick Landmark Selector for Bagalkote
  const landmarkSelect = document.getElementById('quick-landmark');
  const addressInput = document.getElementById('pickup_address');
  const latInput = document.getElementById('latitude');
  const lonInput = document.getElementById('longitude');

  if (landmarkSelect && addressInput && latInput && lonInput) {
    landmarkSelect.addEventListener('change', function () {
      const selected = this.options[this.selectedIndex];
      if (selected.value) {
        addressInput.value = selected.getAttribute('data-address') || selected.text;
        latInput.value = selected.getAttribute('data-lat');
        lonInput.value = selected.getAttribute('data-lon');
        if (typeof updateMapMarker === 'function') {
          updateMapMarker(parseFloat(latInput.value), parseFloat(lonInput.value));
        }
      }
    });
  }

  // 5. GPS Current Location Helper
  const gpsBtn = document.getElementById('btn-get-gps');
  if (gpsBtn && latInput && lonInput) {
    gpsBtn.addEventListener('click', function () {
      if (navigator.geolocation) {
        gpsBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Locating...';
        navigator.geolocation.getCurrentPosition(
          function (position) {
            latInput.value = position.coords.latitude.toFixed(6);
            lonInput.value = position.coords.longitude.toFixed(6);
            gpsBtn.innerHTML = '<i class="bi bi-geo-alt-fill text-success"></i> Located!';
            if (typeof updateMapMarker === 'function') {
              updateMapMarker(position.coords.latitude, position.coords.longitude);
            }
          },
          function (error) {
            alert('Could not access GPS location. Please choose a nearby landmark or enter coordinates.');
            gpsBtn.innerHTML = '<i class="bi bi-geo-alt"></i> Use My GPS';
          }
        );
      } else {
        alert('Geolocation is not supported by your browser.');
      }
    });
  }
});

// Demo Credentials Autofill Helper for Login Page
function fillCredentials(email, password) {
  const emailInput = document.getElementById('email');
  const passInput = document.getElementById('password');
  if (emailInput && passInput) {
    emailInput.value = email;
    passInput.value = password;
  }
}
