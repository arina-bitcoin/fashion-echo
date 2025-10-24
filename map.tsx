// components/map/MapComponent.tsx

import { useState, useCallback } from 'react';
import { YandexMap, Clusterer, Placemark } from 'react-yandex-maps';

interface MapComponentProps {
  listings: Listing[];
  shops: SecondhandShop[];
  onListingClick: (listing: Listing) => void;
  onShopClick: (shop: SecondhandShop) => void;
}

export default function MapComponent({ 
  listings, 
  shops, 
  onListingClick, 
  onShopClick 
}: MapComponentProps) {
  const [mapState, setMapState] = useState({
    center: [55.75, 37.57], // Москва по умолчанию
    zoom: 10
  });

  const getListingIcon = (type: ListingType) => {
    const icons = {
      sale: 'islands#blueCircleDotIcon',
      donate: 'islands#greenCircleDotIcon',
      exchange: 'islands#orangeCircleDotIcon',
      wanted: 'islands#redCircleDotIcon'
    };
    return icons[type];
  };

  return (
    <div className="h-full w-full">
      <YandexMap
        state={mapState}
        width="100%"
        height="100%"
        onBoundsChange={useCallback((e: any) => setMapState(e.get('newState')), [])}
      >
        <Clusterer
          options={{
            preset: 'islands#invertedBlueClusterIcons',
            groupByCoordinates: false,
          }}
        >
          {listings.map((listing) => (
            <Placemark
              key={`listing-${listing.id}`}
              geometry={listing.location.coordinates}
              properties={{
                hintContent: listing.title,
                balloonContent: listing.description,
              }}
              options={{
                preset: getListingIcon(listing.type),
              }}
              onClick={() => onListingClick(listing)}
            />
          ))}
        </Clusterer>
        
        {shops.map((shop) => (
          <Placemark
            key={`shop-${shop.id}`}
            geometry={shop.coordinates}
            properties={{
              hintContent: shop.name,
              balloonContent: `
                <div>
                  <h3>${shop.name}</h3>
                  <p>${shop.address}</p>
                  <p>📞 ${shop.phone}</p>
                  <p>🕒 ${shop.working_hours}</p>
                </div>
              `,
            }}
            options={{
              preset: 'islands#violetShoppingIcon',
            }}
            onClick={() => onShopClick(shop)}
          />
        ))}
      </YandexMap>
    </div>
  );
}