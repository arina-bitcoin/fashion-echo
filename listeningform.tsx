'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { listingSchema, ListingFormData } from '@/lib/validation/listing';

interface ListingFormProps {
  onSubmit: (data: ListingFormData) => Promise<void>;
  initialData?: Partial<ListingFormData>;
}

const CATEGORIES = [
  'Одежда', 'Обувь', 'Аксессуары', 'Детские вещи',
  'Электроника', 'Книги', 'Мебель', 'Другое'
];

export default function ListingForm({ onSubmit, initialData }: ListingFormProps) {
  const [step, setStep] = useState(1);
  const [images, setImages] = useState<File[]>([]);
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch
  } = useForm<ListingFormData>({
    resolver: zodResolver(listingSchema),
    defaultValues: initialData
  });

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setImages(prev => [...prev, ...files]);
  };

  const onFormSubmit = async (data: ListingFormData) => {
    await onSubmit({ ...data, images });
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      {/* Step 1: Основная информация */}
      {step === 1 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Основная информация</h3>
          
          <div>
            <label className="block text-sm font-medium mb-2">Заголовок</label>
            <input
              {...register('title')}
              className="w-full p-2 border rounded"
              placeholder="Например: Детская куртка, размер 110"
            />
            {errors.title && <p className="text-red-500 text-sm">{errors.title.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Описание</label>
            <textarea
              {...register('description')}
              rows={4}
              className="w-full p-2 border rounded"
              placeholder="Опишите состояние вещи, размеры, особенности..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Категория</label>
            <select {...register('category')} className="w-full p-2 border rounded">
              <option value="">Выберите категорию</option>
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <button type="button" onClick={() => setStep(2)} className="btn-primary">
            Далее
          </button>
        </div>
      )}

      {/* Step 2: Фотографии и тип */}
      {step === 2 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Фотографии и тип объявления</h3>
          
          <div>
            <label className="block text-sm font-medium mb-2">Фотографии</label>
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleImageUpload}
              className="w-full p-2 border rounded"
            />
            <div className="flex gap-2 mt-2">
              {images.map((img, index) => (
                <img
                  key={index}
                  src={URL.createObjectURL(img)}
                  alt="Preview"
                  className="w-20 h-20 object-cover rounded"
                />
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Тип объявления</label>
            <select {...register('type')} className="w-full p-2 border rounded">
              <option value="sale">Продажа</option>
              <option value="donate">Отдам даром</option>
              <option value="exchange">Обмен</option>
              <option value="wanted">Ищу</option>
            </select>
          </div>

          {watch('type') === 'sale' && (
            <div>
              <label className="block text-sm font-medium mb-2">Цена (₽)</label>
              <input
                type="number"
                {...register('price', { valueAsNumber: true })}
                className="w-full p-2 border rounded"
                placeholder="0"
              />
            </div>
          )}

          <div className="flex gap-2">
            <button type="button" onClick={() => setStep(1)} className="btn-secondary">
              Назад
            </button>
            <button type="button" onClick={() => setStep(3)} className="btn-primary">
              Далее
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Локация */}
      {step === 3 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Локация</h3>
          
          <div>
            <label className="block text-sm font-medium mb-2">Адрес</label>
            <input
              {...register('address')}
              className="w-full p-2 border rounded"
              placeholder="Введите адрес или выберите на карте"
            />
          </div>

          <div className="h-64 border rounded">
            {/* Мини-карта для выбора локации */}
            <MapComponent
              listings={[]}
              shops={[]}
              onListingClick={() => {}}
              onShopClick={() => {}}
            />
          </div>

          <div className="flex gap-2">
            <button type="button" onClick={() => setStep(2)} className="btn-secondary">
              Назад
            </button>
            <button type="submit" disabled={isSubmitting} className="btn-primary">
              {isSubmitting ? 'Публикую...' : 'Опубликовать'}
            </button>
          </div>
        </div>
      )}
    </form>
  );
}