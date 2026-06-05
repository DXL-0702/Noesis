import path from "path";

export function joinPath(left, right) {
  return path.join(left, right);
}

const logger = function (message) {
  console.log(message);
};

logger(joinPath("src", "index.js"));
