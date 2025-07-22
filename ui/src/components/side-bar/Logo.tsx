import Link from 'next/link';

export default function Logo() {
  return (
    <Link href="/" className="block group">
      <button className="w-full p-2 flex items-center justify-center dark:hover:bg-gray-800 transition-all duration-200 cursor-pointer">
        <div className="w-12 h-12 flex items-center justify-center transform group-hover:scale-110 transition-transform duration-200">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-12 w-12"
            viewBox="0 0 32 32"
            fill="none"
            stroke="#0a8638"
            strokeWidth="1.25"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="0" y="0" width="32" height="32" rx="8" ry="8" fill="#effdf4" stroke="none"/>
            <circle cx="16" cy="8" r="2.5"></circle>
            <circle cx="10" cy="16" r="2.5"></circle>
            <circle cx="22" cy="16" r="2.5"></circle>
            <line x1="16" y1="10.5" x2="16" y2="12.5"></line>
            <line x1="16" y1="12.5" x2="12" y2="14.5"></line>
            <line x1="16" y1="12.5" x2="20" y2="14.5"></line>
            <line x1="10" y1="18.5" x2="10" y2="21.5"></line>
            <line x1="22" y1="18.5" x2="22" y2="21.5"></line>
            <circle cx="10" cy="24" r="2.5"></circle>
            <circle cx="22" cy="24" r="2.5"></circle>
          </svg>
        </div>
      </button>
    </Link>
  );
}
