import React from "react";
import { render } from "./view";

export type UserCardProps = {
  name: string;
};

export function formatName(name: string): string {
  return name.trim().toUpperCase();
}

const UserCard = ({ name }: UserCardProps) => {
  const label = formatName(name);
  render(label);
  return <section>{label}</section>;
};

class UserService {
  load() {
    return fetch("/api/user");
  }
}

export default UserCard;
