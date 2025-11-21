document.addEventListener('DOMContentLoaded', function() {
            populateOffers();
        });

        function populateOffers() {
            const offersContainer = document.getElementById('offers');
            if (!offersContainer) return;
            
            const sampleOffers = [
                { id: 1, name: 'Платье летнее', price: '1200 руб.' },
                { id: 2, name: 'Джинсы классические', price: '800 руб.' },
                { id: 3, name: 'Куртка кожаная', price: '2500 руб.' },
                { id: 4, name: 'Блузка офисная', price: '600 руб.' },
                { id: 5, name: 'Юбка миди', price: '900 руб.' },
                { id: 6, name: 'Свитер шерстяной', price: '1100 руб.' }
            ];
            
            sampleOffers.forEach(offer => {
                const offerElement = document.createElement('div');
                offerElement.className = 'offer';
                offerElement.style.background = 'var(--card-color)';
                offerElement.style.borderRadius = '12px';
                offerElement.style.overflow = 'hidden';
                offerElement.style.boxShadow = 'var(--shadow)';
                
                offerElement.innerHTML = `
                    <img src="https://via.placeholder.com/300x300/F3E4D3/4B0505?text=FASHIONECO" alt="${offer.name}" style="display:block; width:100%; aspect-ratio:1/1; object-fit:cover;">
                    <div style="padding:10px; font-weight:600; color:var(--primary-color);">${offer.name}<br><small>${offer.price}</small></div>
                `;
                
                offersContainer.appendChild(offerElement);
            });
        }