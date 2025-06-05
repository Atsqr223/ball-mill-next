'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { locations, Location as LocationType } from '@/lib/locations'; // Import locations

// Add type to navItems for filtering locations
const navItems = [
  { name: 'Dashboard', href: '/', type: null },
  { name: 'Ball Mill', href: '/ball-mill', type: 'ball-mill' as LocationType['type'] },
  { name: 'Pipeline', href: '/pipeline-monitoring', type: 'pipeline' as LocationType['type'] },
  { name: 'PLC', href: '/plc', type: 'plc' as LocationType['type'] },
  { name: 'Something', href: '/something', type: 'something' as LocationType['type'] },
];

export default function Navbar() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLocationDropdownOpen, setIsLocationDropdownOpen] = useState(false);

  const activeNavItem = navItems.find(item => item.href !== '/' && pathname.startsWith(item.href));
  
  const sectionLocations = activeNavItem && activeNavItem.type
    ? locations.filter(loc => loc.type === activeNavItem.type)
    : [];

  const currentViewedLocationId = (() => {
    if (!activeNavItem || !activeNavItem.type) return null;
    const match = pathname.match(`${activeNavItem.href}/locations/(\d+)`);
    return match ? parseInt(match[1]) : null;
  })();

  const getLinkClassName = (href: string, isActiveOverride?: boolean, isMobile: boolean = false) => {
    const isActive = isActiveOverride !== undefined ? isActiveOverride : (href === '/' ? pathname === href : pathname.startsWith(href));
    let baseClasses = isMobile 
      ? 'block px-3 py-2 rounded-md text-base font-medium'
      : 'px-3 py-2 text-sm font-medium rounded-md';
    
    if (isActive) {
      return `${baseClasses} bg-blue-100 text-blue-700`;
    } else {
      return `${baseClasses} text-gray-700 hover:bg-gray-50 hover:text-gray-900`;
    }
  };
  
  // Close dropdown if path changes
  useEffect(() => {
    setIsLocationDropdownOpen(false);
    setIsMobileMenuOpen(false); // Also close mobile menu on path change
  }, [pathname]);

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link 
              href="/"
              className="text-xl font-bold text-blue-600 hover:text-blue-700 transition-colors"
            >
              Remote Asset Monitoring 
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={getLinkClassName(item.href)}
              >
                {item.name}
              </Link>
            ))}

            {/* Locations Dropdown - Desktop */}
            {activeNavItem && sectionLocations.length > 0 && (
              <div className="relative">
                <button
                  onClick={() => setIsLocationDropdownOpen(prev => !prev)}
                  className={`${getLinkClassName(activeNavItem.href, pathname.startsWith(activeNavItem.href + '/locations/'))} flex items-center space-x-1`}
                >
                  <span>Locations</span>
                  <svg className={`w-4 h-4 transition-transform duration-200 ${isLocationDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {isLocationDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5 z-20">
                    {sectionLocations.map(loc => (
                      <Link
                        key={loc.id}
                        href={`${activeNavItem.href}/locations/${loc.id}`}
                        onClick={() => setIsLocationDropdownOpen(false)}
                        className={`block px-4 py-2 text-sm ${currentViewedLocationId === loc.id ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'}`}
                      >
                        {loc.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMobileMenuOpen(prev => !prev)}
              className="p-2 rounded-md text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
              aria-expanded={isMobileMenuOpen}
              aria-controls="mobile-menu"
            >
              <span className="sr-only">Open main menu</span>
              {isMobileMenuOpen ? (
                <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden" id="mobile-menu">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {navItems.map((item) => (
              <div key={item.name}>
                <Link
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={getLinkClassName(item.href, undefined, true)}
                >
                  {item.name}
                </Link>
                {/* Locations list for mobile - shown if it's the active section */}
                {item.type && activeNavItem?.type === item.type && sectionLocations.length > 0 && (
                  <div className="pl-4 mt-1 space-y-1 border-l-2 border-gray-200 ml-1">
                    {sectionLocations.map(loc => (
                      <Link
                        key={loc.id}
                        href={`${item.href}/locations/${loc.id}`}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={`block px-3 py-2 rounded-md text-sm font-medium ${currentViewedLocationId === loc.id ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'}`}
                      >
                        {loc.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
