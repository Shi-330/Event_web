// static/main.js

// グローバル変数にAPIキーを設定する。
const apiKey = "AIzaSyAnlBfeFmP1oPo8Mil5hJqnajiLqf8wE-M";

function initMap(address = null) {
  const geocoder = new google.maps.Geocoder();
  const mapDiv = document.getElementById("map");

  if (address != null && address.trim() !== "") {
    geocoder.geocode({ address: address }, function (results, status) {
      if (status === "OK") {
        const location = results[0].geometry.location;
        const map = new google.maps.Map(mapDiv, {
          center: location,
          zoom: 15,
        });
        new google.maps.Marker({
          map: map,
          position: location,
        });
      } else {
        mapDiv.textContent = "住所が見つかりませんでした。";
      }
    });
  } else {
    // addressがない場合の処理を追加する。
    const map = new google.maps.Map(mapDiv, {
      center: { lat: 35.681236, lng: 139.767125 }, // 東京駅を中心とする
      zoom: 10,
    });
  }
}
