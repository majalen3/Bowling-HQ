import type { ReactNode } from 'react';

import { NavBar } from './NavBar';

type LayoutProps = {
  children: ReactNode;
};

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app-shell">
      <div className="phone-frame">
        <NavBar />
        <main className="page">{children}</main>
      </div>
    </div>
  );
}
