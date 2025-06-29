"use client";

import { UserButton as ClerkUserButton } from "@clerk/nextjs";

export default function UserButton() {
  return (
    <ClerkUserButton afterSignOutUrl="/" />
  );
}