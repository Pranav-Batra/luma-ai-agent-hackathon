import type { ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DashboardNav } from "@/components/navigation/dashboard-nav";

const usePathname = vi.fn();

vi.mock("next/navigation", () => ({
  usePathname: () => usePathname(),
}));

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    className,
  }: {
    href: string;
    children: ReactNode;
    className?: string;
  }) => (
    <a href={href} className={className}>
      {children}
    </a>
  ),
}));

describe("DashboardNav", () => {
  beforeEach(() => {
    usePathname.mockReset();
  });

  it("highlights the active route", () => {
    usePathname.mockReturnValue("/campaigns");

    render(<DashboardNav />);

    const campaignsLink = screen.getByRole("link", { name: /campaigns/i });
    const analyticsLink = screen.getByRole("link", { name: /analytics/i });

    expect(campaignsLink.className).toContain("bg-[linear-gradient");
    expect(analyticsLink.className).toContain("hover:bg-white/5");
  });
});
