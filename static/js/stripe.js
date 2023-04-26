
console.log("Sanity check!");

// Get Stripe publishable key
fetch("/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

  // new
  // Event handler
  let submitBtn = document.querySelector("#submitBtn");
  if (submitBtn !== null) {
    submitBtn.addEventListener("click", () => {
    // Get Checkout Session ID
    fetch("/create-checkout-session/")
      .then((result) => { return result.json(); })
      .then((data) => {
        console.log(data);
        // Redirect to Stripe Checkout
        return stripe.redirectToCheckout({sessionId: data.sessionId})
      })
      .then((res) => {
        console.log(res);
      });
    });
  }
});


// fetch('/stripe/')
// .then((result) => {return result.json()})
// .then((data) => {
//     const stripe = Stripe(data.publickKey)

//     let subminBtn = document.querySelector('#subminBtn')
//     if(subminBtn !== null){
//         subminBtn.addEventListener('click', () => {
//             fetch('checkout-session')
//             .then((result) => {return result.json()})
//             .then((data) => {
//                 return stripe.redirectToCheckout({sessionId: data.sessionId})
//             })
//             .then((res) => {
//                 console.log('res:', res)
//             })
//         })
//     }
// })