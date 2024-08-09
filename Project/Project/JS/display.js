const restaurantsList = document.getElementById('restaurants-list');

fetch('/api/restaurants')
  .then(response => response.json())
  .then(restaurants => {
    restaurants.forEach(restaurant => {
      const li = document.createElement('li');
      li.innerHTML = `${restaurant.name} <span class="stars">${getStars(restaurant.rating)}</span>`;
      restaurantsList.appendChild(li);
    });
  });

function getStars(rating) {
  const roundedRating = Math.round(rating * 2) / 2;
  const stars = '★'.repeat(Math.floor(roundedRating)) + (roundedRating % 1 > 0 ? '½' : '');
  return `<span class="star">${stars}</span>`;
}
