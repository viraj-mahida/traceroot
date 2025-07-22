import Logo from './Logo';
import Explore from './Explore';
import Line from './Line';
import Profile from './Profile';
import Settings from './Settings';
import Integrate from './Integrate';
import { shouldShowPaymentFeatures } from '@/utils/stripe-config';

export default function Sidebar() {
  const showSettings = shouldShowPaymentFeatures();

  return (
    <aside className="fixed top-0 left-0 h-screen w-[4%] min-w-[60px] bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col justify-between z-50">
      <div className="flex-1 flex flex-col">
        <Logo />
        <Line />
        <Explore />
        <Integrate />
        {/* Only show Settings if Stripe is properly configured */}
        {showSettings && <Settings />}
      </div>
      <Profile />
    </aside>
  );
}
