import Link from 'next/link';
import Image from 'next/image'; // Import Next.js Image component


interface SectionCardProps {
  title: string;
  description: string;
  href: string;
  imageUrl?: string; // Optional image for the card
}

function SectionCard({ title, description, href, imageUrl }: SectionCardProps) {
  return (
    <Link href={href} className="block group">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300 ease-in-out h-full flex flex-col">
        {imageUrl && (
          <div className="w-full h-48 bg-gray-200 overflow-hidden relative"> {/* Added relative positioning for Image fill */}
            <Image 
              src={imageUrl} 
              alt={title} 
              layout="fill" // Makes image fill the container
              objectFit="cover" // Equivalent to object-cover
              className="group-hover:scale-105 transition-transform duration-300 ease-in-out"
            />
          </div>
        )}
        <div className="p-6 flex flex-col flex-grow">
          <h2 className="text-2xl font-semibold mb-2 text-gray-800">{title}</h2>
          <p className="text-gray-600 flex-grow">{description}</p>
          <div className="mt-4">
            <span className="text-blue-500 group-hover:text-blue-700 font-medium">
              Go to {title} &rarr;
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}

const sections = [
  {
    title: 'Ball Mill Monitoring',
    description: 'Monitor various Ball Mill locations, view live streams, and analyze sensor data.',
    href: '/ball-mill',
    imageUrl: '/images/ball-mill.jpg' // Corrected path
  },
  {
    title: 'Pipeline Control & Monitoring',
    description: 'Manage pipeline operations, check for leaks, and monitor sensor readings across different pipeline segments.',
    href: '/pipeline-monitoring', 
    imageUrl: '/images/pipeline.jpg' // Assuming pipeline.png
  },
  {
    title: 'PLC Systems',
    description: 'Oversee Programmable Logic Controllers, view status, and manage configurations. (Coming Soon)',
    href: '/plc',
    imageUrl: '/images/plc.jpg' // Assuming plc.svg
  },
  {
    title: 'Something Else',
    description: 'Future system monitoring and control interface. (Coming Soon)',
    href: '/something',
    imageUrl: '/images/something.jpg' // Assuming something.jpg
  },
];

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-12">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-extrabold text-gray-900 mb-4">Advanced Monitoring Dashboard</h1>
        <p className="text-xl text-gray-600">Select a system below to view detailed information and controls.</p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {sections.map((section) => (
          <SectionCard
            key={section.title}
            title={section.title}
            description={section.description}
            href={section.href}
            imageUrl={section.imageUrl}
          />
        ))}
      </div>
    </div>
  );
}

