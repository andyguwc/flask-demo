var call_checkout = function (event) {
  var plan = event.target.id.split('submit_')[1];
  fetch(`/subscription/stripe_pay?plan=${plan}`)
    .then((result) => {
      return result.json();
    })
    .then((data) => {
      var stripe = Stripe(data.checkout_public_key);
      stripe
        .redirectToCheckout({
          sessionId: data.checkout_session_id,
        })
        .then(function (result) {
          if (result.error) {
            alert(result.error.message);
          }
        })
        .catch(function (error) {
          console.error('Error:', error);
        });
    });
};

document.querySelectorAll('.btn-subscribe').forEach((item) => {
  item.addEventListener('click', call_checkout);
});
