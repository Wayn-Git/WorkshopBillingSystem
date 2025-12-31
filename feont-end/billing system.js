function saveInvoice() {
    let items = [];

    document.querySelectorAll("#serviceTable tr").forEach(row => {
        const service = row.querySelector("input[type='text']").value;
        const price = row.querySelector(".price").value;
        const qty = document.getElementById('Quantity')
        const rat = document.getElementById('Rate')
        const amount = document.getElementById('Amount')

        function calculateAmount() {
            const q = Number(qty.value) || 0;
            const ra = Number(rat.value) || 0;
            amount.value = q * ra;
        }

        qty.addEventListener("input", calculateAmount)
        rat.addEventListener("input", calculateAmount)






        if (service && price) {
            items.push({
                service,
                price
            });
        }
    });

    fetch("/save-invoice", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                items
            })
        })
        .then(res => res.json())
        .then(data => alert(data.message));
}