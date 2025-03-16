function requestDelivery() {
    let data = {
        client_name: $("#client_name").val(),
        pickup_address: $("#pickup_address").val(),
        delivery_address: $("#delivery_address").val()
    };

    $.ajax({
        url: "/request_delivery",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function(response) {
            alert("Pieteikums veiksmīgi pieņemts!");
            $("#client_name, #pickup_address, #delivery_address").val("");
        },
        error: function(error) {
            console.log(error);
            alert("Kļūda, mēģiniet vēlreiz!");
        }
    });
}

function getDeliveries() {
    $.get("/get_deliveries", function(data) {
        $("#delivery_list").empty();
        data.forEach(delivery => {
            $("#delivery_list").append(`<li>${delivery.client_name}: ${delivery.pickup_address} -> ${delivery.delivery_address}</li>`);
        });
    });
}

function generateRoute() {
    $.get("/generate_route", function(response) {
        if (response.error) {
            alert("Nav pietiekami daudz punktu maršruta ģenerēšanai!");
            return;
        }

        let map = new google.maps.Map(document.getElementById("map"), {
            zoom: 10,
            center: { lat: 56.9496, lng: 24.1052 } // Rīga, Latvija
        });

        let directionsService = new google.maps.DirectionsService();
        let directionsRenderer = new google.maps.DirectionsRenderer();
        directionsRenderer.setMap(map);

        let request = {
            origin: response[0].legs[0].start_address,
            destination: response[0].legs[response[0].legs.length - 1].end_address,
            travelMode: "DRIVING"
        };

        directionsService.route(request, function(result, status) {
            if (status === "OK") {
                directionsRenderer.setDirections(result);
            } else {
                alert("Nevar ģenerēt maršrutu: " + status);
            }
        });
    });
}
