'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { locations } from '@/lib/locations';

export default function Navbar() {
  const pathname = usePathname();
  const currentLocation = locations.find(loc => 
    pathname.includes(`/locations/${loc.id}`)
  );

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link 
              href="/"
              className={`text-xl font-bold ${
                pathname === '/' ? 'text-blue-600' : 'text-gray-800'
              } hover:text-blue-500 transition-colors`}
            >
              Ball Mill Monitor
            </Link>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            <div className="relative group">
              <button className="flex items-center space-x-1 px-4 py-2 text-gray-700 hover:text-blue-500 transition-colors">
                <span>Locations</span>
                <svg 
                  className="w-4 h-4" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M19 9l-7 7-7-7" 
                  />
                </svg>
              </button>
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                {locations.map((location) => (
                  <Link
                    key={location.id}
                    href={`/locations/${location.id}`}
                    className={`block px-4 py-2 text-sm ${
                      currentLocation?.id === location.id
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{location.name}</span>
                      <div 
                        className={`w-2 h-2 rounded-full ${
                          location.status === 'active' 
                            ? 'bg-green-500' 
                            : 'bg-red-500'
                        }`} 
                      />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button className="p-2 rounded-md text-gray-700 hover:text-blue-500 focus:outline-none">
              <svg 
                className="h-6 w-6" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M4 6h16M4 12h16m-7 6h7" 
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className="md:hidden">
        <div className="px-2 pt-2 pb-3 space-y-1">
          {locations.map((location) => (
            <Link
              key={location.id}
              href={`/locations/${location.id}`}
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                currentLocation?.id === location.id
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center justify-between">
                <span>{location.name}</span>
                <div 
                  className={`w-2 h-2 rounded-full ${
                    location.status === 'active' 
                      ? 'bg-green-500' 
                      : 'bg-red-500'
                  }`} 
                />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
} 