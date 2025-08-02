// src/components/Layout.tsx

import type { ReactNode } from "react";
import { useLocation, matchPath } from "react-router-dom";
import Header from "./Header";
import "../styles/Layout.scss";

type LayoutProps = {
  children: ReactNode;
  searchQuery?: string;
  setSearchQuery?: (value: string) => void;
};

export default function Layout({
  children,
  searchQuery,
  setSearchQuery,
}: LayoutProps) {
  const location = useLocation();

  const showHeader =
    location.pathname === "/" ||
    matchPath("/course/:id", location.pathname) !== null;

  return (
    <div className="layout">
      <div style={{ height: "1px" }} />
      {showHeader && (
        <Header searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
      )}
      <main>{children}</main>
    </div>
  );
}
